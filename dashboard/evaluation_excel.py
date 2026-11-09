from decimal import Decimal, InvalidOperation
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableColumn, TableFormula, TableStyleInfo
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
            'SUM([@[MID-1 CIA (10)]],[@[MID-1 VIVA (10)]],[@[MID-1 EXAM (10)]])'
        ),
        'MID-2 Total': (
            'SUM([@[MID-2 CIA (10)]],[@[MID-2 VIVA (10)]],[@[MID-2 EXAM (10)]])'
        ),
        'Average MID (30)': 'ROUND(([@[MID-1 Total]]+[@[MID-2 Total]])/2,0)',
        'Total (40)': 'MIN([@[Average MID (30)]]+N([@[PROJECT (10)]]),40)',
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


def _write_summary(worksheet, sheet_number, table_name):
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
            value=f'=IFERROR(TEXTJOIN(", ",TRUE,FILTER({table_name}[Roll No],{table_name}[Grade]=A{offset})),"")',
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
            value=f'=IFERROR(TEXTJOIN(", ",TRUE,FILTER({table_name}[Roll No]&" ("&'
            f'TEXT({table_name}[Attendance]/MAX({table_name}[Attendance])*100,"0.0")&"%)",'
            f'{table_name}[Allocated Attendance Grade]=A{row_number})),"")',
        )
        worksheet.cell(row=row_number, column=4).number_format = '0.0%'
    worksheet['A32'] = 'Total'
    worksheet['D32'] = '=IF(C15=0,0,1)'
    worksheet['D32'].number_format = '0.0%'
    worksheet['E32'] = '=SUM(E25:E31)'

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
        TableColumn(
            id=index,
            name=column,
            calculatedColumnFormula=TableFormula(attr_text=formulae[column]) if column in formulae else None,
        )
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
    _write_summary(summary, sheet_number, table_name)
    workbook.calculation.fullCalcOnLoad = True
    workbook.calculation.forceFullCalc = True
    workbook.calculation.calcMode = 'auto'

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output
