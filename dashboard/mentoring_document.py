"""Build a filled Word mentoring record from the college's supplied template."""

from copy import deepcopy
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.table import Table
from docx.text.paragraph import Paragraph


TEMPLATE_PATH = Path(__file__).parent / "document_templates" / "mentorship_file_b.tech.docx"
SEMESTER_LABELS = [
    ("I B.Tech", "First Semester"),
    ("I B.Tech", "Second Semester"),
    ("II B.Tech", "First Semester"),
    ("II B.Tech", "Second Semester"),
    ("III B.Tech", "First Semester"),
    ("III B.Tech", "Second Semester"),
    ("IV B.Tech", "First Semester"),
    ("IV B.Tech", "Second Semester"),
]


def _text(value):
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.strftime("%d-%m-%Y")
    return str(value).strip()


def _set_cell_text(cell, value):
    """Replace cell text while retaining its existing first-run formatting."""
    paragraphs = cell.paragraphs
    paragraph = paragraphs[0] if paragraphs else cell.add_paragraph()
    runs = paragraph.runs
    if runs:
        first_run = runs[0]
        first_run.text = _text(value)
        for run in runs[1:]:
            run._element.getparent().remove(run._element)
    else:
        paragraph.add_run(_text(value))

    for extra_paragraph in paragraphs[1:]:
        extra_paragraph._element.getparent().remove(extra_paragraph._element)


def _set_xml_cell_text(cell_element, value, parent):
    paragraphs = cell_element.xpath("./w:p")
    if not paragraphs:
        raise ValueError("The mentoring template identity cell has no paragraph.")

    paragraph = Paragraph(paragraphs[0], parent)
    paragraph.clear()
    run = paragraph.add_run(_text(value))
    run.font.name = "Arial"
    run.font.size = Pt(11)


def _semester_heading(semester_number, academic_year=""):
    year_label, semester_label = SEMESTER_LABELS[semester_number - 1]
    academic_year = _text(academic_year)
    year_prefix = f"{academic_year} " if academic_year else ""
    return f"ACADEMIC YEAR: {year_prefix}{year_label}. {semester_label.upper()}"


def _selected_yes_no(value):
    return ("Yes [X]", "No [ ]") if value == "Yes" else ("Yes [ ]", "No [X]") if value == "No" else ("Yes [ ]", "No [ ]")


def _set_semester_radio(row, yes_cell_index, no_cell_index, value):
    yes_text, no_text = _selected_yes_no(value)
    _set_cell_text(row.cells[yes_cell_index], yes_text)
    _set_cell_text(row.cells[no_cell_index], no_text)


def _fill_photograph_placeholder(document, photo_bytes):
    photo_textbox = next(
        (
            textbox for textbox in document._element.xpath(".//w:txbxContent")
            if "photograph" in "".join(
                element.text or ""
                for element in textbox.iter()
                if element.tag == qn("w:t")
            ).casefold()
        ),
        None,
    )
    if photo_textbox is None:
        raise ValueError("The supplied mentoring template has no Photograph placeholder.")

    photo_paragraph_element = next(
        (
            paragraph for paragraph in photo_textbox.iter()
            if paragraph.tag == qn("w:p")
            and "photograph" in "".join(
                element.text or ""
                for element in paragraph.iter()
                if element.tag == qn("w:t")
            ).casefold()
        ),
        None,
    )
    if photo_paragraph_element is None:
        raise ValueError("The mentoring template Photograph placeholder has no text paragraph.")

    for paragraph in list(photo_textbox):
        if paragraph.tag == qn("w:p") and paragraph is not photo_paragraph_element:
            photo_textbox.remove(paragraph)

    photo_paragraph = Paragraph(photo_paragraph_element, document._body)
    photo_paragraph.clear()
    photo_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture = photo_paragraph.add_run().add_picture(
        BytesIO(photo_bytes),
        width=Inches(1.8),
        height=Inches(2.16),
    )
    picture._inline.docPr.set("descr", "Student photograph")


def _add_continuation_semester(
    document,
    semester_number,
    semester_data,
    template_semester_table,
    template_slots_table,
    template_signoff_table,
):
    document.add_page_break()

    semester_element = deepcopy(template_semester_table._tbl)
    semester_rows = semester_element.xpath("./w:tr")
    for row in semester_rows[:5]:
        semester_element.remove(row)
    document._element.body.append(semester_element)
    semester_table = Table(semester_element, document._body)
    _set_cell_text(
        semester_table.rows[0].cells[0],
        _semester_heading(semester_number, semester_data.get("academic_year")),
    )
    _set_cell_text(semester_table.rows[1].cells[2], semester_data.get("mentor_name"))
    _set_cell_text(semester_table.rows[1].cells[8], semester_data.get("designation"))
    _set_cell_text(
        semester_table.rows[3].cells[0],
        f"{_text(semester_data.get('start_date'))}\n"
        f"SEMESTER ATTENDANCE: {_text(semester_data.get('attendance'))}",
    )
    _set_cell_text(semester_table.rows[3].cells[4], semester_data.get("end_date"))
    _set_semester_radio(semester_table.rows[4], 3, 7, semester_data.get("is_hosteller"))
    _set_semester_radio(semester_table.rows[5], 3, 7, semester_data.get("college_bus"))
    _set_semester_radio(semester_table.rows[6], 3, 7, semester_data.get("backlogs"))
    _set_cell_text(semester_table.rows[7].cells[3], semester_data.get("backlog_courses"))
    _set_cell_text(semester_table.rows[8].cells[3], semester_data.get("support_required"))

    slots_element = deepcopy(template_slots_table._tbl)
    document._element.body.append(slots_element)
    slots_table = Table(slots_element, document._body)
    for slot_number, row_index in ((1, 1), (2, 2)):
        slot = f"slot{slot_number}"
        for column_index, suffix in ((1, "observations"), (2, "suggestions"), (3, "progress")):
            _set_cell_text(
                slots_table.rows[row_index].cells[column_index],
                semester_data.get(f"{slot}_{suffix}"),
            )

    signoff_element = deepcopy(template_signoff_table._tbl)
    document._element.body.append(signoff_element)
    signoff_table = Table(signoff_element, document._body)
    for row_index, field_name in ((0, "date_of_mentoring"), (1, "mentee_sign"), (2, "mentor_sign")):
        _set_cell_text(signoff_table.rows[row_index].cells[1], semester_data.get(field_name))
    _set_cell_text(
        signoff_table.rows[4].cells[0],
        f"Signature of AC: {_text(semester_data.get('signature_ac'))}    "
        f"Signature of HOD: {_text(semester_data.get('signature_hod'))}",
    )


def create_mentoring_document(student, mentoring, photo_bytes=None, student_name="", hall_ticket_no=""):
    """Return a populated B.Tech mentoring record as DOCX bytes."""
    if not TEMPLATE_PATH.is_file():
        raise FileNotFoundError("The B.Tech mentoring Word template is missing.")

    document = Document(TEMPLATE_PATH)
    tables = document.tables
    if len(tables) < 11:
        raise ValueError("The supplied mentoring template has an unexpected table layout.")

    semester_data = mentoring.semester_data if isinstance(mentoring.semester_data, dict) else {}
    student_name = student_name or _text(getattr(student, "student_name", ""))
    hall_ticket = hall_ticket_no or _text(getattr(student, "ht_no", ""))
    branch = _text(getattr(mentoring, "branch", ""))
    batch = _text(getattr(mentoring, "batch", ""))
    admission_year = _text(getattr(mentoring, "admission_year", ""))

    # Student information sheet and identity details.
    _set_cell_text(tables[0].rows[0].cells[0], f"BATCH: {batch}")
    info = tables[1]
    _set_cell_text(info.rows[2].cells[2], batch)
    _set_cell_text(info.rows[2].cells[9], admission_year)
    identity_labels = (
        "Hall Ticket No.",
        "Name of the Student",
        "Program",
        "Branch / Specialization",
    )
    identity_table = next(
        (
            table
            for table in document._element.xpath(".//w:tbl")
            if len(table.xpath("./w:tr")) == len(identity_labels)
            and tuple(
                "".join(text.text or "" for text in row.xpath("./w:tc[1]//w:t")).strip()
                for row in table.xpath("./w:tr")
            )
            == identity_labels
        ),
        None,
    )
    if identity_table is None:
        raise ValueError("The supplied mentoring template has no student identity table.")

    identity_values = (hall_ticket, student_name, "B.Tech", branch)
    for row, value in zip(identity_table.xpath("./w:tr"), identity_values):
        cells = row.xpath("./w:tc")
        if len(cells) != 2:
            raise ValueError("The mentoring template identity table has an unexpected layout.")
        _set_xml_cell_text(cells[1], value, document._body)

    identity_cell = info.rows[3].cells[0]
    status_paragraph = identity_cell.add_paragraph(
        f"Re-admitted Student: {_text(mentoring.readmitted_student)}    "
        f"Lateral Entry Student: {_text(mentoring.lateral_entry_student)}"
    )
    for run in status_paragraph.runs:
        run.font.name = "Arial"
        run.font.size = Pt(9)
    if photo_bytes:
        _fill_photograph_placeholder(document, photo_bytes)
    _set_cell_text(info.rows[6].cells[5], mentoring.father_name)
    _set_cell_text(info.rows[8].cells[5], mentoring.mother_name)
    _set_cell_text(info.rows[11].cells[0], mentoring.address)
    _set_cell_text(info.rows[11].cells[3], mentoring.permanent_address)
    _set_cell_text(info.rows[11].cells[7], mentoring.communication_address)

    # Personal and contact details.
    _set_cell_text(tables[2].rows[1].cells[0], mentoring.gender)
    _set_cell_text(tables[2].rows[1].cells[1], mentoring.blood_group)
    _set_cell_text(tables[2].rows[1].cells[2], mentoring.allergies)
    _set_cell_text(tables[3].rows[1].cells[1], mentoring.student_mobile)
    _set_cell_text(tables[3].rows[1].cells[2], mentoring.student_email)
    _set_cell_text(tables[3].rows[2].cells[1], mentoring.parent_mobile)
    _set_cell_text(tables[3].rows[2].cells[2], mentoring.parent_email)

    # Educational background and grade summary.
    for row_index, prefix in ((1, "ssc"), (2, "inter")):
        fields = (
            f"{prefix}_school_name" if prefix == "ssc" else "inter_college_name",
            f"{prefix}_place" if prefix == "ssc" else "inter_place",
            f"{prefix}_board" if prefix == "ssc" else "inter_board",
            f"{prefix}_percentage" if prefix == "ssc" else "inter_percentage",
        )
        for cell_index, field_name in enumerate(fields, start=1):
            _set_cell_text(tables[4].rows[row_index].cells[cell_index], getattr(mentoring, field_name))

    for semester_number in range(1, 9):
        _set_cell_text(tables[5].rows[2].cells[semester_number], getattr(mentoring, f"sgpa_sem{semester_number}"))
        _set_cell_text(tables[5].rows[3].cells[semester_number], getattr(mentoring, f"cgpa_sem{semester_number}"))

    # Semester I details are built into the supplied template.
    sem1 = semester_data.get("1", {})
    sem1_table = tables[6]
    _set_cell_text(sem1_table.rows[0].cells[0], _semester_heading(1, sem1.get("academic_year")))
    _set_cell_text(sem1_table.rows[1].cells[1], sem1.get("mentor_name"))
    _set_cell_text(sem1_table.rows[1].cells[8], sem1.get("designation"))
    _set_cell_text(
        sem1_table.rows[3].cells[0],
        f"From: {_text(sem1.get('start_date'))}    To: {_text(sem1.get('end_date'))}\n"
        f"SEMESTER ATTENDANCE: {_text(sem1.get('attendance'))}",
    )
    _set_semester_radio(sem1_table.rows[4], 2, 6, sem1.get("is_hosteller"))
    _set_semester_radio(sem1_table.rows[5], 2, 6, sem1.get("college_bus"))
    _set_cell_text(sem1_table.rows[9].cells[7], sem1.get("support_required"))
    for slot_number, row_index in ((1, 1), (2, 2)):
        slot = f"slot{slot_number}"
        for column_index, suffix in ((1, "observations"), (2, "suggestions"), (3, "progress")):
            _set_cell_text(tables[7].rows[row_index].cells[column_index], sem1.get(f"{slot}_{suffix}"))
    sem1_signoff = tables[8]
    for row_index, field_name in ((0, "date_of_mentoring"), (1, "mentee_sign"), (2, "mentor_sign")):
        _set_cell_text(sem1_signoff.rows[row_index].cells[1], sem1.get(field_name))
    _set_cell_text(
        sem1_signoff.rows[4].cells[0],
        f"Signature of AC: {_text(sem1.get('signature_ac'))}    Signature of HOD: {_text(sem1.get('signature_hod'))}",
    )

    # Semester II details are built into the supplied template.
    sem2 = semester_data.get("2", {})
    _set_cell_text(sem1_signoff.rows[6].cells[2], sem2.get("mentor_name"))
    _set_cell_text(sem1_signoff.rows[6].cells[8], sem2.get("designation"))
    _set_cell_text(
        sem1_signoff.rows[5].cells[0],
        _semester_heading(2, sem2.get("academic_year")),
    )
    _set_cell_text(
        sem1_signoff.rows[8].cells[0],
        f"{_text(sem2.get('start_date'))}\n"
        f"SEMESTER ATTENDANCE: {_text(sem2.get('attendance'))}",
    )
    _set_cell_text(sem1_signoff.rows[8].cells[4], sem2.get("end_date"))
    _set_semester_radio(sem1_signoff.rows[9], 3, 7, sem2.get("is_hosteller"))
    _set_semester_radio(sem1_signoff.rows[10], 3, 7, sem2.get("college_bus"))
    _set_semester_radio(sem1_signoff.rows[11], 3, 7, sem2.get("backlogs"))
    _set_cell_text(sem1_signoff.rows[12].cells[3], sem2.get("backlog_courses"))
    _set_cell_text(sem1_signoff.rows[13].cells[3], sem2.get("support_required"))
    for slot_number, row_index in ((1, 1), (2, 2)):
        slot = f"slot{slot_number}"
        for column_index, suffix in ((1, "observations"), (2, "suggestions"), (3, "progress")):
            _set_cell_text(tables[9].rows[row_index].cells[column_index], sem2.get(f"{slot}_{suffix}"))
    for row_index, field_name in ((0, "date_of_mentoring"), (1, "mentee_sign"), (2, "mentor_sign")):
        _set_cell_text(tables[10].rows[row_index].cells[1], sem2.get(field_name))
    _set_cell_text(
        tables[10].rows[4].cells[0],
        f"Signature of AC: {_text(sem2.get('signature_ac'))}    Signature of HOD: {_text(sem2.get('signature_hod'))}",
    )

    # The first-semester part of the supplied template has no backlog fields.
    extra_heading = document.add_paragraph()
    extra_heading.paragraph_format.space_before = Pt(8)
    extra_heading.paragraph_format.space_after = Pt(3)
    extra_heading_run = extra_heading.add_run("I B.Tech - First Semester Additional Details")
    extra_heading_run.bold = True
    extra_heading_run.font.name = "Arial"
    extra_heading_run.font.size = Pt(10)
    extra_table = document.add_table(rows=2, cols=2)
    extra_table.style = "Table Grid"
    extra_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row, (label, value) in zip(
        extra_table.rows,
        (("Backlogs in previous Semester", sem1.get("backlogs")), ("Backlog Courses", sem1.get("backlog_courses"))),
    ):
        row.cells[0].width = Inches(2.15)
        row.cells[1].width = Inches(4.0)
        _set_cell_text(row.cells[0], label)
        _set_cell_text(row.cells[1], value)

    # Repeat the complete mentoring form layout for the remaining semesters.
    for semester_number in range(3, 9):
        _add_continuation_semester(
            document,
            semester_number,
            semester_data.get(str(semester_number), {}),
            sem1_signoff,
            tables[9],
            tables[10],
        )

    output = BytesIO()
    document.save(output)
    return output.getvalue()
