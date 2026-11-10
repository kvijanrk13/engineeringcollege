from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from io import BytesIO
import re
import zipfile
from xml.etree import ElementTree

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableColumn, TableStyleInfo
from openpyxl.utils import get_column_letter


CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
GRADE_ROWS = (
    ('O', '37-40'),
    ('A+', '32-36'),
    ('A', '28-31'),
    ('B+', '24-27'),
    ('B', '20-23'),
    ('P', '14-19'),
    ('F', '0-13'),
)
ATTENDANCE_ALLOCATION = (
    ('O', 0.15, '10 - 15%', '17%'),
    ('A+', 0.25, '20 - 25%', '28%'),
    ('A', 0.25, '20 - 25%', '28%'),
    ('B+', 0.25, '20 - 25%', '28%'),
    ('LOWER', 0.10, '10 - 15%', '17%'),
)
ATTENDANCE_SUMMARY_ROWS = (
    ('O', '10 - 15%', '17%'),
    ('A+', '20 - 25%', '28%'),
    ('A', '20 - 25%', '28%'),
    ('B+', '20 - 25%', '28%'),
    ('B', '10 - 15%', '17%'),
    ('P', '', ''),
    ('F', '', ''),
)


class EvaluationExportError(ValueError):
    pass


def _text(value, label, maximum=100):
    if value is None:
        return ''
    if not isinstance(value, (str, int, float)):
        raise EvaluationExportError(f'{label} must be text.')
    result = str(value).strip()
    if len(result) > maximum:
        raise EvaluationExportError(f'{label} is too long.')
    if any(ord(character) < 32 or ord(character) == 127 for character in result):
        raise EvaluationExportError(f'{label} contains unsupported control characters.')
    return result


def _score(value, label, maximum, allow_absent=False, allow_decimal=False):
    if value is None or value == '':
        return None
    if allow_absent and isinstance(value, str) and value.strip().upper() == 'AB':
        return 'AB'
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise EvaluationExportError(f'{label} must be a number' + (' or AB.' if allow_absent else '.'))
    if not parsed.is_finite() or parsed < 0 or parsed > maximum:
        raise EvaluationExportError(f'{label} must be between 0 and {maximum}.')
    if not allow_decimal and parsed != parsed.to_integral_value():
        raise EvaluationExportError(f'{label} must be a whole number.')
    return int(parsed) if parsed == parsed.to_integral_value() else float(parsed)


def _validated_rows(sheet_number, rows):
    if not isinstance(rows, list) or not rows or len(rows) > 1000:
        raise EvaluationExportError('The evaluation must contain between 1 and 1000 student rows.')

    fields = (
        ('attendance', 100000, False),
        ('mid1Obj', 10, True),
        ('mid1Desc', 20, False),
        ('mid2Obj', 10, True),
        ('mid2Desc', 20, False),
        ('assignment', 5, False),
        ('viva', 5, False),
    ) if sheet_number in {'1', '2'} else (
        ('attendance', 100000, False),
        ('mid1Cia', 10, False),
        ('mid1Viva', 10, False),
        ('mid1Exam', 10, False),
        ('mid2Cia', 10, False),
        ('mid2Viva', 10, False),
        ('mid2Exam', 10, False),
        ('project', 10, False),
    )
    validated = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise EvaluationExportError(f'Student row {index} must be an object.')
        student = {'rollNo': _text(row.get('rollNo'), f'Roll number in row {index}', 64)}
        for field, maximum, allow_absent in fields:
            student[field] = _score(
                row.get(field),
                f'{field} in row {index}',
                maximum,
                allow_absent=allow_absent,
                allow_decimal=field == 'attendance',
            )
        validated.append(student)
    return validated


def _write_text(cell, value):
    cell.value = value
    cell.data_type = 's'


def _format_sheet_title(worksheet, title, column_count):
    worksheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=column_count)
    title_cell = worksheet.cell(row=1, column=1, value=title)
    title_cell.font = Font(bold=True, color='FFFFFF', size=16)
    title_cell.fill = PatternFill('solid', fgColor='17324D')
    title_cell.alignment = Alignment(horizontal='center')
    worksheet.row_dimensions[1].height = 28


def _attendance_formulas(table_name, attendance_column, attendance_grade_column, rank_column):
    allocation_start = 17
    allocation_end = allocation_start + len(ATTENDANCE_ALLOCATION) - 1
    quota_refs = [f'Summary!$F${allocation_start + index}' for index in range(4)]
    cumulative = []
    running = []
    for reference in quota_refs:
        running.append(reference)
        cumulative.append('SUM(' + ','.join(running) + ')')

    attendance_ref = f'{table_name}[{attendance_column}]'
    row_attendance = f'[@[{attendance_column}]]'
    rank_formula = (
        f'IF({row_attendance}="","",COUNTIF({attendance_ref},">"&{row_attendance})'
        f'+COUNTIF(INDEX({attendance_ref},1):{row_attendance},{row_attendance}))'
    )
    rank_ref = f'[@[{rank_column}]]'
    max_attendance = f'MAX({attendance_ref})'
    ratio = f'{row_attendance}/{max_attendance}'
    lower_grade = (
        f'IF({max_attendance}=0,"B",IF({ratio}>=0.5,"B",'
        f'IF({ratio}>=0.4,"P","F")))'
    )
    grade_formula = (
        f'IF({row_attendance}="","",IF({rank_ref}<=Summary!$F${allocation_start},"O",'
        f'IF({rank_ref}<={cumulative[1]},"A+",'
        f'IF({rank_ref}<={cumulative[2]},"A",'
        f'IF({rank_ref}<={cumulative[3]},"B+",{lower_grade})))))'
    )
    return {
        rank_column: rank_formula,
        attendance_grade_column: grade_formula,
    }


def _evaluation_columns(sheet_number):
    if sheet_number in {'1', '2'}:
        columns = [
            'Roll No', 'Attendance', 'Attendance Based Marks Grade',
            'MID-1 Obj (10)', 'MID-1 Desc (20)', 'MID-1 Total',
            'MID-2 Obj (10)', 'MID-2 Desc (20)', 'MID-2 Total',
            'Average MID (30)', 'Assignment (5)', 'Viva (5)',
            'Total (40)', 'Percentage', 'Grade',
        ]
        input_fields = (
            '[@[MID-1 Obj (10)]],[@[MID-1 Desc (20)]],[@[MID-2 Obj (10)]],'
            '[@[MID-2 Desc (20)]],[@[Assignment (5)]],[@[Viva (5)]]'
        )
        formulae = {
            'Attendance Based Marks Grade': (
                'IF([@Attendance]="","",IF(MAX(Evaluation' + sheet_number
                + 'Marks[Attendance])=0,"-",IF([@Attendance]/MAX(Evaluation'
                + sheet_number + 'Marks[Attendance])>=0.9,"O",IF([@Attendance]/MAX(Evaluation'
                + sheet_number + 'Marks[Attendance])>=0.8,"A+",IF([@Attendance]/MAX(Evaluation'
                + sheet_number + 'Marks[Attendance])>=0.7,"A",IF([@Attendance]/MAX(Evaluation'
                + sheet_number + 'Marks[Attendance])>=0.6,"B+",IF([@Attendance]/MAX(Evaluation'
                + sheet_number + 'Marks[Attendance])>=0.5,"B",IF([@Attendance]/MAX(Evaluation'
                + sheet_number + 'Marks[Attendance])>=0.4,"P","F"))))))))'
            ),
            'MID-1 Total': (
                'IF([@[Evaluation Entered]]="","",'
                'SUM([@[MID-1 Obj (10)]],[@[MID-1 Desc (20)]]))'
            ),
            'MID-2 Total': (
                'IF([@[Evaluation Entered]]="","",'
                'SUM([@[MID-2 Obj (10)]],[@[MID-2 Desc (20)]]))'
            ),
            'Average MID (30)': (
                'IF([@[Evaluation Entered]]="","",'
                'ROUND((N([@[MID-1 Total]])+N([@[MID-2 Total]]))/2,0))'
            ),
            'Total (40)': (
                'IF([@[Evaluation Entered]]="","",MIN(N([@[Average MID (30)]])'
                '+N([@[Assignment (5)]])+N([@[Viva (5)]]),40))'
            ),
            'Percentage': (
                'IF([@[Total (40)]]="","",[@[Total (40)]]/40)'
            ),
            'Grade': (
                'IF([@[Total (40)]]="","",IF([@[Total (40)]]>=37,"O",'
                'IF([@[Total (40)]]>=32,"A+",IF([@[Total (40)]]>=28,"A",'
                'IF([@[Total (40)]]>=24,"B+",IF([@[Total (40)]]>=20,"B",'
                'IF([@[Total (40)]]>=14,"P","F")))))))'
            ),
        }
        formulae['Evaluation Entered'] = f'IF(COUNTA({input_fields})=0,"",1)'
        if sheet_number == '2':
            formulae['MID-1 Desc (20)'] = (
                'IF(OR([@Attendance]="",[@[MID-1 Obj (10)]]="",'
                '[@[MID-2 Obj (10)]]="",[@[Assignment (5)]]="",[@[Viva (5)]]=""),"",'
                'MIN(16,MAX(ROUND(MAX(0,MIN(100,[@Attendance]))*16/100,0),'
                '2*(30-[@[Assignment (5)]]-[@[Viva (5)]])-1-[@[MID-1 Obj (10)]])))'
            )
            formulae['MID-2 Desc (20)'] = '0'
        columns.extend(('Evaluation Entered', 'Attendance Rank', 'Allocated Attendance Grade'))
        formulae.update(_attendance_formulas(
            f'Evaluation{sheet_number}Marks',
            'Attendance',
            'Allocated Attendance Grade',
            'Attendance Rank',
        ))
        return columns, formulae

    columns = [
        'Roll No', 'Attendance', 'Attendance Based Marks Grade',
        'MID-1 CIA (10)', 'MID-1 VIVA (10)', 'MID-1 EXAM (10)', 'MID-1 Total',
        'MID-2 CIA (10)', 'MID-2 VIVA (10)', 'MID-2 EXAM (10)', 'MID-2 Total',
        'Average MID (30)', 'PROJECT (10)', 'Total (40)', 'Grade',
    ]
    formulae = {
        'Attendance Based Marks Grade': (
            'IF([@Attendance]="","",IF(MAX(Evaluation' + sheet_number
            + 'Marks[Attendance])=0,"-",IF([@Attendance]/MAX(Evaluation'
            + sheet_number + 'Marks[Attendance])>=0.9,"O",IF([@Attendance]/MAX(Evaluation'
            + sheet_number + 'Marks[Attendance])>=0.8,"A+",IF([@Attendance]/MAX(Evaluation'
            + sheet_number + 'Marks[Attendance])>=0.7,"A",IF([@Attendance]/MAX(Evaluation'
            + sheet_number + 'Marks[Attendance])>=0.6,"B+",IF([@Attendance]/MAX(Evaluation'
            + sheet_number + 'Marks[Attendance])>=0.5,"B",IF([@Attendance]/MAX(Evaluation'
            + sheet_number + 'Marks[Attendance])>=0.4,"P","F"))))))))'
        ),
        'MID-1 Total': (
            (
                'IF(COUNTA([@[MID-1 CIA (10)]],[@[MID-1 VIVA (10)]],'
                '[@[MID-1 EXAM (10)]])=0,"",'
                'SUM([@[MID-1 CIA (10)]],[@[MID-1 VIVA (10)]],[@[MID-1 EXAM (10)]]))'
                if sheet_number == '3'
                else 'SUM([@[MID-1 CIA (10)]],[@[MID-1 VIVA (10)]],[@[MID-1 EXAM (10)]])'
            )
        ),
        'MID-2 Total': (
            (
                'IF(COUNTA([@[MID-2 CIA (10)]],[@[MID-2 VIVA (10)]],'
                '[@[MID-2 EXAM (10)]])=0,"",'
                'SUM([@[MID-2 CIA (10)]],[@[MID-2 VIVA (10)]],[@[MID-2 EXAM (10)]]))'
                if sheet_number == '3'
                else 'SUM([@[MID-2 CIA (10)]],[@[MID-2 VIVA (10)]],[@[MID-2 EXAM (10)]])'
            )
        ),
        'Average MID (30)': (
            'IF(COUNTA([@[MID-1 CIA (10)]],[@[MID-1 VIVA (10)]],'
            '[@[MID-1 EXAM (10)]],[@[MID-2 CIA (10)]],[@[MID-2 VIVA (10)]],'
            '[@[MID-2 EXAM (10)]])=0,"",'
            'ROUND((N([@[MID-1 Total]])+N([@[MID-2 Total]]))/2,0))'
            if sheet_number == '3'
            else 'ROUND(([@[MID-1 Total]]+[@[MID-2 Total]])/2,0)'
        ),
        'Total (40)': (
            'IF(COUNTA([@[MID-1 CIA (10)]],[@[MID-1 VIVA (10)]],'
            '[@[MID-1 EXAM (10)]],[@[MID-2 CIA (10)]],[@[MID-2 VIVA (10)]],'
            '[@[MID-2 EXAM (10)]],[@[PROJECT (10)]])=0,"",'
            'MIN(N([@[Average MID (30)]])+N([@[PROJECT (10)]]),40))'
            if sheet_number == '3'
            else 'MIN([@[Average MID (30)]]+N([@[PROJECT (10)]]),40)'
        ),
        'Grade': (
            'IF(COUNTA([@[MID-1 CIA (10)]],[@[MID-1 VIVA (10)]],'
            '[@[MID-1 EXAM (10)]],[@[MID-2 CIA (10)]],[@[MID-2 VIVA (10)]],'
            '[@[MID-2 EXAM (10)]],[@[PROJECT (10)]])=0,"",'
            'IF([@[Total (40)]]>=37,"O",IF([@[Total (40)]]>=32,"A+",'
            'IF([@[Total (40)]]>=28,"A",IF([@[Total (40)]]>=24,"B+",'
            'IF([@[Total (40)]]>=20,"B",IF([@[Total (40)]]>=14,"P","F")))))))'
            if sheet_number == '3'
            else 'IF([@[Total (40)]]>=37,"O",IF([@[Total (40)]]>=32,"A+",'
            'IF([@[Total (40)]]>=28,"A",IF([@[Total (40)]]>=24,"B+",'
            'IF([@[Total (40)]]>=20,"B",IF([@[Total (40)]]>=14,"P","F"))))))'
        ),
    }
    if sheet_number == '3':
        formulae['MID-1 Entered'] = (
            'IF(COUNTA([@[MID-1 CIA (10)]],[@[MID-1 VIVA (10)]],'
            '[@[MID-1 EXAM (10)]])=0,"",1)'
        )
        formulae['MID-2 Entered'] = (
            'IF(COUNTA([@[MID-2 CIA (10)]],[@[MID-2 VIVA (10)]],'
            '[@[MID-2 EXAM (10)]])=0,"",1)'
        )
    else:
        formulae['MID-1 Entered'] = '1'
        formulae['MID-2 Entered'] = '1'
    columns.extend(('Attendance Rank', 'Allocated Attendance Grade', 'MID-1 Entered', 'MID-2 Entered'))
    formulae.update(_attendance_formulas(
        f'Evaluation{sheet_number}Marks',
        'Attendance',
        'Allocated Attendance Grade',
        'Attendance Rank',
    ))
    return columns, formulae


def _rounded_excel(value):
    return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def _grade_for_total(total):
    for grade, lower_bound in (
        ('O', 37), ('A+', 32), ('A', 28), ('B+', 24), ('B', 20), ('P', 14),
    ):
        if total >= lower_bound:
            return grade
    return 'F'


def _formula_cache_values(sheet_number, students, columns):
    attendance_values = [student['attendance'] for student in students if student['attendance'] is not None]
    attendance_count = len(attendance_values)
    maximum_attendance = max(attendance_values, default=0)

    bases = [int(attendance_count * share) for _, share, _, _ in ATTENDANCE_ALLOCATION]
    remainders = [
        attendance_count * share - base
        for base, (_, share, _, _) in zip(bases, ATTENDANCE_ALLOCATION)
    ]
    remaining = attendance_count - sum(bases)
    for index in sorted(range(len(remainders)), key=lambda item: (-remainders[item], item))[:remaining]:
        bases[index] += 1
    attendance_quotas = bases

    row_results = []
    previous_attendance = []
    for student in students:
        attendance = student['attendance']
        attendance_rank = None
        attendance_grade = ''
        if attendance is not None:
            attendance_rank = sum(value > attendance for value in attendance_values)
            attendance_rank += sum(value == attendance for value in previous_attendance) + 1
            previous_attendance.append(attendance)
            quota_ends = []
            for quota in attendance_quotas[:4]:
                quota_ends.append(quota + (quota_ends[-1] if quota_ends else 0))
            if attendance_rank <= quota_ends[0]:
                attendance_grade = 'O'
            elif attendance_rank <= quota_ends[1]:
                attendance_grade = 'A+'
            elif attendance_rank <= quota_ends[2]:
                attendance_grade = 'A'
            elif attendance_rank <= quota_ends[3]:
                attendance_grade = 'B+'
            elif maximum_attendance == 0 or attendance / maximum_attendance >= 0.5:
                attendance_grade = 'B'
            elif attendance / maximum_attendance >= 0.4:
                attendance_grade = 'P'
            else:
                attendance_grade = 'F'

        result = {
            'Roll No': student['rollNo'],
            'Attendance': attendance,
            'Attendance Rank': attendance_rank if attendance_rank is not None else '',
            'Allocated Attendance Grade': attendance_grade,
        }
        if attendance is None:
            attendance_marks_grade = ''
        elif maximum_attendance == 0:
            attendance_marks_grade = '-'
        else:
            ratio = attendance / maximum_attendance
            attendance_marks_grade = next(
                (grade for grade, threshold in (
                    ('O', 0.9), ('A+', 0.8), ('A', 0.7),
                    ('B+', 0.6), ('B', 0.5), ('P', 0.4),
                ) if ratio >= threshold),
                'F',
            )
        result['Attendance Based Marks Grade'] = attendance_marks_grade

        if sheet_number in {'1', '2'}:
            fields = ('mid1Obj', 'mid1Desc', 'mid2Obj', 'mid2Desc', 'assignment', 'viva')
            entered = any(student[field] is not None for field in fields)
            mid1_desc = student['mid1Desc']
            mid2_desc = student['mid2Desc']
            if sheet_number == '2':
                mid1_desc = None
                if all(student[field] is not None for field in (
                    'attendance', 'mid1Obj', 'mid2Obj', 'assignment', 'viva',
                )):
                    target = _rounded_excel(max(0, min(100, student['attendance'])) * 16 / 100)
                    cap = 2 * (30 - student['assignment'] - student['viva']) - 1 - student['mid1Obj']
                    mid1_desc = min(16, max(target, cap))
                mid2_desc = 0

            def excel_sum(*values):
                return sum(value for value in values if isinstance(value, (int, float)))

            mid1_total = excel_sum(student['mid1Obj'], mid1_desc) if entered else ''
            mid2_total = excel_sum(student['mid2Obj'], mid2_desc) if entered else ''
            mid_average = _rounded_excel(
                (
                    (mid1_total if isinstance(mid1_total, (int, float)) else 0)
                    + (mid2_total if isinstance(mid2_total, (int, float)) else 0)
                ) / 2
            ) if entered else ''
            if entered:
                total = min(
                    mid_average
                    + (student['assignment'] or 0)
                    + (student['viva'] or 0),
                    40,
                )
                grade = _grade_for_total(total)
                percentage = total / 40
            else:
                total = grade = percentage = ''
            result.update({
                'MID-1 Obj (10)': student['mid1Obj'],
                'MID-1 Desc (20)': mid1_desc,
                'MID-1 Total': mid1_total,
                'MID-2 Obj (10)': student['mid2Obj'],
                'MID-2 Desc (20)': mid2_desc,
                'MID-2 Total': mid2_total,
                'Average MID (30)': mid_average,
                'Assignment (5)': student['assignment'],
                'Viva (5)': student['viva'],
                'Total (40)': total,
                'Percentage': percentage,
                'Grade': grade,
                'Evaluation Entered': 1 if entered else '',
            })
        else:
            mid1_values = [student[field] for field in ('mid1Cia', 'mid1Viva', 'mid1Exam')]
            mid2_values = [student[field] for field in ('mid2Cia', 'mid2Viva', 'mid2Exam')]
            mid1_entered = any(value is not None for value in mid1_values)
            mid2_entered = any(value is not None for value in mid2_values)
            mid1_total = sum(value or 0 for value in mid1_values) if mid1_entered or sheet_number == '4' else ''
            mid2_total = sum(value or 0 for value in mid2_values) if mid2_entered or sheet_number == '4' else ''
            mid_average = (
                _rounded_excel(
                    (
                        (mid1_total if isinstance(mid1_total, (int, float)) else 0)
                        + (mid2_total if isinstance(mid2_total, (int, float)) else 0)
                    ) / 2
                )
                if mid1_entered or mid2_entered or sheet_number == '4'
                else ''
            )
            any_marks = mid1_entered or mid2_entered or student['project'] is not None
            total = (
                min(
                    (mid_average if isinstance(mid_average, (int, float)) else 0)
                    + (student['project'] or 0),
                    40,
                )
                if any_marks or sheet_number == '4'
                else ''
            )
            grade = _grade_for_total(total) if sheet_number == '4' or any_marks else ''
            result.update({
                'MID-1 CIA (10)': student['mid1Cia'],
                'MID-1 VIVA (10)': student['mid1Viva'],
                'MID-1 EXAM (10)': student['mid1Exam'],
                'MID-1 Total': mid1_total,
                'MID-2 CIA (10)': student['mid2Cia'],
                'MID-2 VIVA (10)': student['mid2Viva'],
                'MID-2 EXAM (10)': student['mid2Exam'],
                'MID-2 Total': mid2_total,
                'Average MID (30)': mid_average,
                'PROJECT (10)': student['project'],
                'Total (40)': total,
                'Grade': grade,
                'MID-1 Entered': 1 if sheet_number == '4' or mid1_entered else '',
                'MID-2 Entered': 1 if sheet_number == '4' or mid2_entered else '',
            })
        row_results.append(result)

    graded_rows = [row for row in row_results if row['Grade'] != '']
    if sheet_number == '3':
        class_average = (
            sum(row['Total (40)'] for row in graded_rows) / len(graded_rows) / 40
            if graded_rows else 0
        )
    else:
        class_average = sum(
            row['Total (40)'] if isinstance(row['Total (40)'], (int, float)) else 0
            for row in row_results
        ) / max(len(row_results), 1) / 40
    mid1_rows = [row for row in row_results if row.get('MID-1 Entered') == 1]
    mid2_rows = [row for row in row_results if row.get('MID-2 Entered') == 1]
    mid1_average = (
        sum(row['MID-1 Total'] for row in mid1_rows) / len(mid1_rows) / 30
        if mid1_rows else 0
    )
    mid2_average = (
        sum(row['MID-2 Total'] for row in mid2_rows) / len(mid2_rows) / 30
        if mid2_rows else 0
    )
    summary_values = {
        'B3': class_average,
        'D3': mid1_average,
        'F3': mid2_average,
        'B4': (
            sum(row['Total (40)'] for row in graded_rows) / len(graded_rows) / 40
            if graded_rows else 0
        ),
    }

    for index, (grade, _) in enumerate(GRADE_ROWS, start=6):
        matching = [row for row in row_results if row['Grade'] == grade]
        summary_values[f'C{index}'] = len(matching)
        summary_values[f'D{index}'] = len(matching) / len(graded_rows) if graded_rows else 0
        summary_values[f'E{index}'] = ', '.join(row['Roll No'] for row in matching)
    summary_values['C13'] = len(graded_rows)
    summary_values['D13'] = 1 if graded_rows else 0
    summary_values['C15'] = attendance_count

    for index, ((_, share, _, _), base) in enumerate(zip(ATTENDANCE_ALLOCATION, bases), start=17):
        summary_values[f'C{index}'] = attendance_count
        summary_values[f'D{index}'] = int(attendance_count * share)
        summary_values[f'E{index}'] = attendance_count * share - int(attendance_count * share)
        summary_values[f'F{index}'] = base
    for index, (grade, _, _) in enumerate(ATTENDANCE_SUMMARY_ROWS, start=25):
        matching = [row for row in row_results if row['Allocated Attendance Grade'] == grade]
        summary_values[f'D{index}'] = len(matching) / attendance_count if attendance_count else 0
        summary_values[f'E{index}'] = len(matching)
        summary_values[f'F{index}'] = ', '.join(
            f"{row['Roll No']} ({row['Attendance'] / maximum_attendance * 100:.1f}%)"
            for row in matching
        ) if maximum_attendance else ''
    summary_values['D32'] = 1 if attendance_count else 0
    summary_values['E32'] = attendance_count

    return {
        'xl/worksheets/sheet1.xml': {
            f'{get_column_letter(column)}{row_number}': result.get(columns[column - 1], '')
            for row_number, result in enumerate(row_results, start=5)
            for column in range(1, len(columns) + 1)
            if columns[column - 1] in result
        },
        'xl/worksheets/sheet2.xml': summary_values,
    }


def _formula_for_data_row(formula, row_number, columns, table_name, last_row):
    attendance_column = get_column_letter(columns.index('Attendance') + 1)
    formula = formula.replace(
        f'INDEX({table_name}[Attendance],1):[@[Attendance]]',
        f'{attendance_column}$5:{attendance_column}{row_number}',
    )
    table_column_pattern = re.compile(re.escape(table_name) + r'\[([^\]]+)\]')
    formula = table_column_pattern.sub(
        lambda match: (
            f'{get_column_letter(columns.index(match.group(1)) + 1)}$5:'
            f'{get_column_letter(columns.index(match.group(1)) + 1)}${last_row}'
        ),
        formula,
    )
    formula = re.sub(
        r'\[@\[([^\]]+)\]\]',
        lambda match: f'{get_column_letter(columns.index(match.group(1)) + 1)}{row_number}',
        formula,
    )
    return re.sub(
        r'\[@([^\]]+)\]',
        lambda match: f'{get_column_letter(columns.index(match.group(1)) + 1)}{row_number}',
        formula,
    )


def _write_formula_caches(output, values_by_sheet):
    # Keep formula results visible in viewers that do not calculate Excel formulas.
    namespace = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    ElementTree.register_namespace('', namespace)
    rewritten = BytesIO()
    with zipfile.ZipFile(output, 'r') as source, zipfile.ZipFile(rewritten, 'w', zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            contents = source.read(item.filename)
            sheet_values = values_by_sheet.get(item.filename)
            if sheet_values:
                root = ElementTree.fromstring(contents)
                for cell in root.findall(f'.//{{{namespace}}}c'):
                    formula = cell.find(f'{{{namespace}}}f')
                    if formula is None or cell.attrib.get('r') not in sheet_values:
                        continue
                    value = sheet_values[cell.attrib['r']]
                    cached = cell.find(f'{{{namespace}}}v')
                    if cached is None:
                        cached = ElementTree.SubElement(cell, f'{{{namespace}}}v')
                    if isinstance(value, str):
                        cell.attrib['t'] = 'str'
                        cached.text = value
                    else:
                        cell.attrib.pop('t', None)
                        cached.text = str(value)
                contents = ElementTree.tostring(root, encoding='utf-8', xml_declaration=True)
            target.writestr(item, contents)
    rewritten.seek(0)
    output.seek(0)
    output.truncate()
    output.write(rewritten.getvalue())
    output.seek(0)


def _write_summary(worksheet, sheet_number, table_name, last_row):
    _format_sheet_title(worksheet, f'Internal Evaluation {sheet_number} Summary', 6)
    worksheet['A3'] = 'Class Average (%)'
    worksheet['A3'].font = Font(bold=True)
    class_average_formula = (
        f'AVERAGEIF({table_name}[Grade],"<>",{table_name}[Total (40)])'
        if sheet_number == '3'
        else f'SUM({table_name}[Total (40)])/ROWS({table_name}[Roll No])'
    )
    worksheet['B3'] = f'=IFERROR(({class_average_formula})/40,0)'
    worksheet['B3'].number_format = '0.0%'
    worksheet['C3'] = 'MID-1 Average Achieved'
    worksheet['C3'].font = Font(bold=True)
    worksheet['D3'] = f'=IFERROR(AVERAGEIF({table_name}[MID-1 Entered],1,{table_name}[MID-1 Total])/30,0)'
    worksheet['D3'].number_format = '0.0%'
    worksheet['E3'] = 'MID-2 Average Achieved'
    worksheet['E3'].font = Font(bold=True)
    worksheet['F3'] = f'=IFERROR(AVERAGEIF({table_name}[MID-2 Entered],1,{table_name}[MID-2 Total])/30,0)'
    worksheet['F3'].number_format = '0.0%'
    worksheet['A4'] = 'Total Average Achieved'
    worksheet['A4'].font = Font(bold=True)
    worksheet['B4'] = f'=IFERROR(AVERAGEIF({table_name}[Grade],"<>",{table_name}[Total (40)])/40,0)'
    worksheet['B4'].number_format = '0.0%'

    grade_headers = ['Grade', 'Total (out of 40)', 'Student Count', 'Percent of Graded Students', 'Roll Numbers']
    for column, value in enumerate(grade_headers, start=1):
        cell = worksheet.cell(row=5, column=column, value=value)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='2F75B5')
    for offset, (grade, score_range) in enumerate(GRADE_ROWS, start=6):
        worksheet.cell(row=offset, column=1, value=grade)
        worksheet.cell(row=offset, column=2, value=score_range)
        worksheet.cell(row=offset, column=3, value=f'=COUNTIF({table_name}[Grade],A{offset})')
        worksheet.cell(row=offset, column=4, value=f'=IFERROR(C{offset}/SUM($C$6:$C$12),0)')
        worksheet.cell(
            row=offset,
            column=5,
            value=f'={get_column_letter(7 + offset - 6)}${last_row - 3}',
        )
        worksheet.cell(row=offset, column=4).number_format = '0.0%'
    worksheet['A13'] = 'Total graded'
    worksheet['C13'] = '=SUM(C6:C12)'
    worksheet['D13'] = '=IF(C13=0,0,1)'
    worksheet['D13'].number_format = '0.0%'

    for column, value in enumerate(
        ['Grade band', 'Distribution share', 'Students with Attendance', 'Base Count', 'Remainder', 'Allocated Count'],
        start=1,
    ):
        cell = worksheet.cell(row=16, column=column, value=value)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='2F75B5')
    worksheet['A15'] = 'Attendance allocation'
    worksheet['A15'].font = Font(bold=True)
    worksheet['C15'] = f'=COUNT({table_name}[Attendance])'
    for row_number, (grade, share, _, _) in enumerate(ATTENDANCE_ALLOCATION, start=17):
        worksheet.cell(row=row_number, column=1, value=grade)
        worksheet.cell(row=row_number, column=2, value=share).number_format = '0%'
        worksheet.cell(row=row_number, column=3, value='=$C$15')
        worksheet.cell(row=row_number, column=4, value=f'=ROUNDDOWN(C{row_number}*B{row_number},0)')
        worksheet.cell(row=row_number, column=5, value=f'=MOD(C{row_number}*B{row_number},1)')
        remainder_rank = (
            f'SUMPRODUCT(--($E$17:$E$21>E{row_number}))'
            f'+COUNTIF($E$17:E{row_number},E{row_number})-1'
        )
        worksheet.cell(
            row=row_number,
            column=6,
            value=f'=D{row_number}+IF($C$15-SUM($D$17:$D$21)>{remainder_rank},1,0)',
        )
        worksheet.cell(row=row_number, column=5).number_format = '0.000'

    attendance_headers = [
        'Grade', 'Students Count out of Total Given %', "Can't Go Beyond",
        'Allocated % by Faculty', 'Student Count', 'Students',
    ]
    for column, value in enumerate(attendance_headers, start=1):
        cell = worksheet.cell(row=24, column=column, value=value)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='2F75B5')
    for row_number, (grade, expected, limit) in enumerate(ATTENDANCE_SUMMARY_ROWS, start=25):
        worksheet.cell(row=row_number, column=1, value=grade)
        worksheet.cell(row=row_number, column=2, value=expected)
        worksheet.cell(row=row_number, column=3, value=limit)
        worksheet.cell(row=row_number, column=5, value=f'=COUNTIF({table_name}[Allocated Attendance Grade],A{row_number})')
        worksheet.cell(row=row_number, column=4, value=f'=IFERROR(E{row_number}/$C$15,0)')
        worksheet.cell(
            row=row_number,
            column=6,
            value=f'={get_column_letter(14 + row_number - 25)}${last_row - 3}',
        )
        worksheet.cell(row=row_number, column=4).number_format = '0.0%'
    worksheet['A32'] = 'Total'
    worksheet['D32'] = '=IF(C15=0,0,1)'
    worksheet['D32'].number_format = '0.0%'
    worksheet['E32'] = '=SUM(E25:E31)'

    columns, _ = _evaluation_columns(sheet_number)
    roll_column = get_column_letter(columns.index('Roll No') + 1)
    attendance_column = get_column_letter(columns.index('Attendance') + 1)
    grade_column = get_column_letter(columns.index('Grade') + 1)
    attendance_grade_column = get_column_letter(columns.index('Allocated Attendance Grade') + 1)
    source_sheet = f"'Evaluation {sheet_number}'"
    capacity = last_row - 4
    grade_helper_start = 7
    attendance_helper_start = grade_helper_start + len(GRADE_ROWS)
    for index, (grade, _) in enumerate(GRADE_ROWS):
        helper_column = grade_helper_start + index
        helper_letter = get_column_letter(helper_column)
        worksheet.cell(row=1, column=helper_column, value=f'Grade {grade} roll numbers')
        for helper_row, source_row in enumerate(range(5, last_row + 1), start=2):
            previous = f'{helper_letter}{helper_row - 1}'
            worksheet.cell(
                row=helper_row,
                column=helper_column,
                value=(
                    f'=IF({source_sheet}!${grade_column}${source_row}=$A${index + 6},'
                    f'IF({previous}="",{source_sheet}!${roll_column}${source_row},'
                    f'{previous}&", "&{source_sheet}!${roll_column}${source_row}),{previous})'
                ),
            )
    for index, (grade, _, _) in enumerate(ATTENDANCE_SUMMARY_ROWS):
        helper_column = attendance_helper_start + index
        helper_letter = get_column_letter(helper_column)
        worksheet.cell(row=1, column=helper_column, value=f'Attendance {grade} students')
        for helper_row, source_row in enumerate(range(5, last_row + 1), start=2):
            previous = f'{helper_letter}{helper_row - 1}'
            student = (
                f'{source_sheet}!${roll_column}${source_row}&" ("&TEXT('
                f'IFERROR({source_sheet}!${attendance_column}${source_row}/'
                f'MAX({source_sheet}!${attendance_column}$5:{source_sheet}!'
                f'${attendance_column}${last_row})*100,0),"0.0")&"%)"'
            )
            worksheet.cell(
                row=helper_row,
                column=helper_column,
                value=(
                    f'=IF({source_sheet}!${attendance_grade_column}${source_row}'
                    f'=$A${index + 25},'
                    f'IF({previous}="",{student},{previous}&", "&{student}),{previous})'
                ),
            )
    for column in range(grade_helper_start, attendance_helper_start + len(ATTENDANCE_SUMMARY_ROWS)):
        worksheet.column_dimensions[get_column_letter(column)].hidden = True

    for column, width in enumerate((16, 30, 20, 23, 18, 60), start=1):
        worksheet.column_dimensions[get_column_letter(column)].width = width
    worksheet.freeze_panes = 'A6'
    worksheet.sheet_view.showGridLines = False

    attendance_validation = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', allow_blank=True)
    attendance_validation.error = 'Attendance must be zero or a positive number.'
    attendance_validation.errorTitle = 'Invalid attendance'
    attendance_validation.showErrorMessage = True
    worksheet.add_data_validation(attendance_validation)
    attendance_validation.add('B5:B1004')


def create_evaluation_workbook(sheet_number, subject_name, rows):
    if str(sheet_number) not in {'1', '2', '3', '4'}:
        raise EvaluationExportError('Choose an Internal Evaluation from 1 through 4.')
    sheet_number = str(sheet_number)
    subject_name = _text(subject_name, 'Subject name', 150)
    students = _validated_rows(sheet_number, rows)
    if sheet_number == '3':
        students.extend(
            {
                'rollNo': '',
                'attendance': None,
                'mid1Cia': None,
                'mid1Viva': None,
                'mid1Exam': None,
                'mid2Cia': None,
                'mid2Viva': None,
                'mid2Exam': None,
                'project': None,
            }
            for _ in range(1000 - len(students))
        )

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = f'Evaluation {sheet_number}'
    summary = workbook.create_sheet('Summary')
    columns, formulae = _evaluation_columns(sheet_number)
    table_name = f'Evaluation{sheet_number}Marks'
    _format_sheet_title(worksheet, f'Internal Evaluation {sheet_number} - {subject_name}', len(columns))
    worksheet['A2'] = 'Subject'
    worksheet['A2'].font = Font(bold=True)
    _write_text(worksheet['B2'], subject_name)
    for column_number, label in enumerate(columns, start=1):
        cell = worksheet.cell(row=4, column=column_number, value=label)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='2F75B5')
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    worksheet.row_dimensions[4].height = 36

    for row_number, student in enumerate(students, start=5):
        values = [student['rollNo'], student['attendance']]
        if sheet_number in {'1', '2'}:
            values.extend([
                None,
                student['mid1Obj'],
                student['mid1Desc'] if sheet_number == '1' else None,
                None,
                student['mid2Obj'],
                student['mid2Desc'] if sheet_number == '1' else None,
                None,
                None,
                student['assignment'],
                student['viva'],
                None,
                None,
                None,
                None,
                None,
                None,
            ])
        else:
            values.extend([
                None,
                student['mid1Cia'],
                student['mid1Viva'],
                student['mid1Exam'],
                None,
                student['mid2Cia'],
                student['mid2Viva'],
                student['mid2Exam'],
                None,
                None,
                student['project'],
                None,
                None,
                None,
                None,
                None,
                None,
            ])
        for column_number, value in enumerate(values, start=1):
            cell = worksheet.cell(row=row_number, column=column_number, value=value)
            if column_number == 1:
                _write_text(cell, student['rollNo'])
            if cell.data_type != 'f':
                cell.alignment = Alignment(vertical='center')
        for field in formulae:
            cell = worksheet.cell(row=row_number, column=columns.index(field) + 1)
            cell.value = '=' + formulae[field]
            cell.alignment = Alignment(vertical='center')

    last_row = 4 + len(students)
    table = Table(displayName=table_name, ref=f'A4:{get_column_letter(len(columns))}{last_row}')
    table.tableColumns = [
        TableColumn(id=index, name=column)
        for index, column in enumerate(columns, start=1)
    ]
    table.tableStyleInfo = TableStyleInfo(
        name='TableStyleMedium2',
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    worksheet.add_table(table)
    for row_number in range(5, last_row + 1):
        for field, formula in formulae.items():
            cell = worksheet.cell(row=row_number, column=columns.index(field) + 1)
            cell.value = '=' + _formula_for_data_row(
                formula,
                row_number,
                columns,
                table_name,
                last_row,
            )
    if sheet_number in {'1', '2'}:
        input_columns = {'E': 20, 'H': 20, 'K': 5, 'L': 5}
        if sheet_number == '2':
            input_columns = {'K': 5, 'L': 5}
    else:
        input_columns = {'D': 10, 'E': 10, 'F': 10, 'H': 10, 'I': 10, 'J': 10, 'M': 10}
    for column, maximum in input_columns.items():
        validation = DataValidation(type='decimal', operator='between', formula1='0', formula2=str(maximum))
        validation.allow_blank = True
        validation.error = f'Enter a number from 0 to {maximum}.'
        validation.errorTitle = 'Invalid mark'
        validation.showErrorMessage = True
        worksheet.add_data_validation(validation)
        validation.add(f'{column}5:{column}1004')
    if sheet_number in {'1', '2'}:
        for column in ('D', 'G'):
            validation = DataValidation(
                type='custom',
                formula1=f'=OR(AND(ISNUMBER({column}5),{column}5>=0,{column}5<=10),{column}5="AB",{column}5="")',
                allow_blank=True,
            )
            validation.error = 'Enter a mark from 0 to 10 or AB.'
            validation.errorTitle = 'Invalid objective mark'
            validation.showErrorMessage = True
            worksheet.add_data_validation(validation)
            validation.add(f'{column}5:{column}1004')

    for index, label in enumerate(columns, start=1):
        worksheet.column_dimensions[get_column_letter(index)].width = 16
        if label == 'Roll No':
            worksheet.column_dimensions[get_column_letter(index)].width = 18
        elif label in {'Attendance Based Marks Grade', 'Allocated Attendance Grade'}:
            worksheet.column_dimensions[get_column_letter(index)].width = 24
        elif label == 'Attendance Rank':
            worksheet.column_dimensions[get_column_letter(index)].hidden = True
        elif label in {'Evaluation Entered', 'MID-1 Entered', 'MID-2 Entered'}:
            worksheet.column_dimensions[get_column_letter(index)].hidden = True
    worksheet.freeze_panes = 'A5'
    worksheet.sheet_view.showGridLines = False
    _write_summary(summary, sheet_number, table_name, last_row)
    workbook.calculation.fullCalcOnLoad = True
    workbook.calculation.forceFullCalc = True
    workbook.calculation.calcMode = 'auto'

    output = BytesIO()
    workbook.save(output)
    _write_formula_caches(output, _formula_cache_values(sheet_number, students, columns))
    output.seek(0)
    return output
