"""Editable table layouts transcribed from the supplied NBA Annexure II."""


def _table(key, title, columns, row_labels=()):
    rows = [[label, *([""] * (len(columns) - 1))] for label in row_labels]
    if not rows:
        rows = [[""] * len(columns)]
    return {"key": f"annexure_{key}", "title": title, "columns": columns, "rows": rows}


NBA_ANNEXURE_TABLES = {
    1: [
        _table("1_2_2_1", "Table No. 1.2.2.1: Details of courses and teaching-learning scheme", ["Course Code", "Course Title", "CI: L", "CI: T", "CI: P", "Lab Instruction", "Term Work", "Self Learning", "Total Hours / Semester", "Credits"]),
        _table("1_3_3_1", "Table No. 1.3.3.1: Program curriculum grouping by components", ["Curriculum Component", "Content (% of program credits)", "Contact Hours", "Credits"], ["Basic Sciences", "Basic Engineering", "Humanities and Social Sciences", "Program Core", "Program Electives", "Open Electives", "Project(s)", "Internships / Seminars", "Any other", "Total number of credits"]),
        _table("1_3_1", "Table No. 1.3.1: Connection of courses with POs / PSOs", ["PO / PSO Number", "List of Courses"], [*(f"PO{i}" for i in range(1, 12)), *(f"PSO{i}" for i in range(1, 4))]),
        _table("1_4_1_1", "Table No. 1.4.1.1: Course outcomes", ["Course Outcome No.", "Course Outcome Statement"], [f"CO{i}" for i in range(1, 7)]),
        _table("1_4_2", "Table No. 1.4.2: Course articulation matrix", ["Course Outcome Code and Statement", *(f"PO{i}" for i in range(1, 12)), *(f"PSO{i}" for i in range(1, 4))], [f"CO{i}" for i in range(1, 7)]),
        _table("1_5_1", "Table No. 1.5.1: Program articulation matrix", ["Course Code", "Course Name", *(f"PO{i}" for i in range(1, 12)), *(f"PSO{i}" for i in range(1, 4))]),
    ],
    2: [],  # Criterion 2 contains narrative prompts and no prescribed tables.
    3: [
        _table("3_8_1", "Table No. 3.8.1: PO / PSO attainment using direct assessment", ["Course", *(f"PO{i}" for i in range(1, 12)), *(f"PSO{i}" for i in range(1, 4))], ["C101", "C102", "C201", "C202", "C301", "C302", "C401", "C402", "Direct Attainment"]),
        _table("3_8_2", "Table No. 3.8.2: PO / PSO attainment using indirect assessment", ["Name of Survey", *(f"PO{i}" for i in range(1, 12)), *(f"PSO{i}" for i in range(1, 4))], ["Survey 1", "Survey 2", "Survey 3", "Indirect Attainment"]),
        _table("3_8_3", "Table No. 3.8.3: Overall PO / PSO attainment", ["Assessment", *(f"PO{i}" for i in range(1, 12)), *(f"PSO{i}" for i in range(1, 4))], ["Direct Attainment", "Indirect Attainment", "Overall Attainment"]),
    ],
    4: [
        _table("4A", "Table No. 4A: Admission details excluding multiple entry / exit", ["Item", "CAY", "CAYm1", "CAYm2", "CAYm3", "CAYm4", "CAYm5", "CAYm6"], ["N: Sanctioned intake", "N1: First-year admissions", "N2: Lateral-entry admissions", "N3: Separate division", "N4: Supernumerary admissions", "Total admitted (N1+N2+N3+N4)"]),
        _table("4B", "Table No. 4B: Admission and exit through multiple entry / exit", ["Item", "CAY", "CAYm1", "CAYm2", "CAYm3", "CAYm4", "CAYm5", "CAYm6"], ["N52: Admitted in second year", "N53: Admitted in third year", "N54: Admitted in fourth year", "N5: Total multiple entry", "N61: Exited after first year", "N62: Exited after second year", "N63: Exited after third year", "N6: Total multiple exit"]),
        _table("4C", "Table No. 4C: Graduates within the stipulated period", ["Year of Entry", "Total Students", "I Year Graduates", "II Year Graduates", "III Year Graduates", "IV Year Graduates"], ["CAY", "CAYm1", "CAYm2", "CAYm3", "CAYm4 (LYG)", "CAYm5 (LYGm1)", "CAYm6 (LYGm2)"]),
        _table("4_1_1", "Table No. 4.1.1: First-year student enrolment ratio", ["Item", "CAY", "CAYm1", "CAYm2"], ["N: Sanctioned intake", "N1: First-year admissions", "N4: Supernumerary admissions", "Enrolment Ratio (ER)", "Average ER"]),
        _table("4_1_2", "Table No. 4.1.2: Marks distribution for enrolment ratio", ["Enrolment Ratio Band", "Marks"], [">= 90%", ">= 80%", ">= 70%", ">= 60%", ">= 50%", ">= 40%"]),
        _table("4_2_1", "Table No. 4.2.1: Success rate in stipulated period", ["Item", "LYG", "LYGm1", "LYGm2"], ["A: Eligible admitted students", "B: Graduated within stipulated duration", "Success Rate (B/A)", "Average SR"]),
        *[_table(f"4_{year}_1", f"Table No. 4.{year}.1: Academic performance index, year {year-2}", ["Academic Performance", "CAYm1", "CAYm2", "CAYm3"], ["X: Mean GPA / marks index", "Y: Successful students", "Z: Students appeared", "API = X*(Y/Z)", "Average API"]) for year in (3, 4, 5)],
        _table("4_6_1", "Table No. 4.6.1: Placement, higher studies and entrepreneurship", ["Item", "LYG", "LYGm1", "LYGm2"], ["FS: Final-year students", "X: Students placed", "Y: Higher studies", "Z: Entrepreneurship", "X+Y+Z", "Placement Index", "Average Index"]),
        _table("4_7_1_1", "Table No. 4.7.1.1: Active professional societies / bodies / clubs", ["S.N.", "Name of Society / Body / Chapter / Club"]),
        _table("4_7_1_2", "Table No. 4.7.1.2: Events and programs organized", ["S.N.", "Society / Body / Chapter / Club", "Event", "National / International", "Date"]),
        _table("4_7_2_1", "Table No. 4.7.2.1: Students participating in professional events", ["S.N.", "Student", "Event", "State / National / International", "Date", "Award"]),
        _table("4_7_3_1", "Table No. 4.7.3.1: Students involved in departmental publications", ["S.N.", "Journal / Magazine / Newsletter", "Editor", "Student and Semester", "Issues", "Hard / Soft Copy"]),
        _table("4_7_4_1", "Table No. 4.7.4.1: Student publications", ["S.N.", "Student and Semester", "Publisher", "Journal / Conference", "Volume and Issue", "Award"]),
    ],
    5: [
        _table("5A", "Table No. 5A: Faculty details", ["S.N.", "Faculty Name", "PAN", "APAAR / Faculty ID", "Highest Degree", "University", "Specialization", "Institution Joining Date", "Department Joining Date", "Experience", "Joining Designation", "Present Designation", "Professor Designation Date", "Association Type", "Full / Part Time", "Currently Associated", "Leaving Date"]),
        _table("5_1_2", "Table No. 5.1.2: Student-faculty ratio", ["Program / Measure", "CAY", "CAYm1", "CAYm2"], ["UG program student counts", "PG program student counts", "DS: Department students", "AS: Allied department students", "S: Total students", "DF: Department faculty", "AF: Allied faculty", "F: Total faculty", "PoP", "FF: First-year-only load", "TF: Total faculty", "SFR", "Average SFR"]),
        _table("5_2_1", "Table No. 5.2.1: Faculty qualification", ["Year", "X: PhD Faculty", "Y: Masters Faculty", "RF", "FQI"], ["CAY", "CAYm1", "CAYm2", "Average Assessment"]),
        _table("5_3_1", "Table No. 5.3.1: Faculty cadre proportion", ["Year", "Professors Required", "Professors Available", "Associate Professors Required", "Associate Professors Available", "Assistant Professors Required", "Assistant Professors Available"], ["CAY", "CAYm1", "CAYm2", "Average", "Numbers", "Cadre Proportion Marks"]),
        _table("5_4_1", "Table No. 5.4.1: Visiting / adjunct faculty and teaching loads", ["S.N.", "Name", "Designation and Organization", "Course Handled", "Hours"], ["CAYm1", "CAYm2", "CAYm3"]),
        _table("5_5_1", "Table No. 5.5.1: Faculty retention ratio", ["Item", "CAY", "CAYm1", "CAYm2"], ["RF: Required faculty", "AF: Available faculty", "A: <1 year", "B: 1–2 years", "C: 2–3 years", "D: 3–4 years", "E: >4 years", "Faculty Retention (FR)", "Average FR"]),
    ],
    6: [
        _table("6_1_1_1", "Table No. 6.1.1.1: Faculty professional memberships", ["S.N.", "Faculty Name", "Professional Society / Body", "National / International Level", "Grade / Position"]),
        _table("6_1_2_1_1", "Table No. 6.1.2.1.1: Faculty as STTP / FDP resource persons", ["S.N.", "Faculty Resource Person", "STTP / FDP", "Date", "Location", "Organizer"], ["CAYm1", "CAYm2", "CAYm3"]),
        _table("6_1_2_2_1", "Table No. 6.1.2.2.1: Faculty participation in STTP / FDP", ["S.N.", "Faculty Participant", "CAYm1 Points", "CAYm2 Points", "CAYm3 Points", "Sum"]),
        _table("6_1_3_1", "Table No. 6.1.3.1: Faculty-developed MOOC courses", ["S.N.", "Faculty Name", "Course Developed", "Online Platform / Link"]),
        _table("6_1_4_1", "Table No. 6.1.4.1: Faculty MOOC certifications", ["S.N.", "Faculty Name", "Course", "Offered By", "Grade"]),
        _table("6_1_5_1", "Table No. 6.1.5.1: Department FDP / STTP programs", ["S.N.", "Program Name", "Date", "Duration", "Speaker", "Designation / Organization", "People Attended"], ["CAYm1", "CAYm2", "CAYm3"]),
        _table("6_1_6_1", "Table No. 6.1.6.1: Faculty support in student innovative projects", ["S.N.", "Faculty", "Event", "Date", "Place", "Website Link"], ["CAYm1", "CAYm2", "CAYm3"]),
        _table("6_1_7_1", "Table No. 6.1.7.1: Faculty industry internship / training / collaboration", ["S.N.", "Faculty", "Internship / Training / Collaboration", "Company and Place", "Duration", "Outcomes"]),
        _table("6_2_1_1", "Table No. 6.2.1.1: Faculty publication details", ["S.N.", "Publication Item", "CAYm1", "CAYm2", "CAYm3"], ["Peer-reviewed journal papers", "Peer-reviewed conference papers", "Books / book chapters"]),
        _table("6_2_2_1", "Table No. 6.2.2.1: Ph.D. details", ["S.N.", "Item", "CAYm1", "CAYm2", "CAYm3"], ["Students enrolled for Ph.D.", "Ph.D. students graduated"]),
        *[_table(f"6_2_{n}_1", f"Table No. 6.2.{n}.1: {title}", ["S.N.", "PI / Faculty", "Co-PI", "Department", "Project Title", "Funding Agency", "Duration", "Amount (Lacs)", "Amount Received / Utilized", "Outcome"], ["CAYm1", "CAYm2", "CAYm3", "Total for three years"]) for n, title in ((4, "Sponsored research projects"), (5, "Consultancy projects"), (6, "Seed money / internal research grants"))],
    ],
    7: [
        _table("7_1_1", "Table No. 7.1.1: Laboratories and technical manpower", ["S.N.", "Laboratory", "Student Batch Size", "Major Equipment", "Weekly Utilization", "Technical Staff Name", "Designation", "Qualification"]),
        _table("7_2_1", "Table No. 7.2.1: Additional laboratory facilities", ["S.N.", "Facility Name", "Details", "Purpose", "Utilization", "Relevance to POs / PSOs"]),
        _table("7_4_1", "Table No. 7.4.1: Laboratory safety measures", ["S.N.", "Laboratory", "Safety Measures"]),
        _table("7_5_1", "Table No. 7.5.1: Project / research labs and Centres of Excellence", ["S.N.", "Laboratory / Centre Name"]),
    ],
    8: [
        _table("8_3_1", "Table No. 8.3.1: Improvement in faculty qualification and publications", ["Item", "CAYm1", "CAYm2", "CAYm3"], ["Faculty members with Ph.D.", "Peer-reviewed journal publications", "Conference publications"]),
        _table("8_4_1", "Table No. 8.4.1: Improvement in academic performance", ["Item", "CAYm1", "CAYm2", "CAYm3"], ["First-year Academic Performance Index", "Second-year Academic Performance Index", "Third-year Academic Performance Index"]),
    ],
    9: [
        _table("9_1_1", "Table No. 9.1.1: First-year student-faculty ratio", ["Year", "Sanctioned Intake (S4)", "Required Faculty (RF4)", "Basic Science / Humanities Faculty (NS1)", "Engineering Science Faculty (NS2)", "Percentage / FYSFR"], ["CAY", "CAYm1", "CAYm2", "Average Percentage"]),
        _table("9_7_1", "Table No. 9.7.1: Institute-level budget summary", ["Financial Year", "Fee Income", "Government Grants", "Other Sources", "Total Income", "Actual Expenditure", "Students", "Expenditure per Student"], ["CFYm1", "CFYm2", "CFYm3"]),
        _table("9_7_2", "Table No. 9.7.2: Institute-level budget and expenditure", ["Item", "Budget CFY", "Actual CFY", "Budget CFYm1", "Actual CFYm1", "Budget CFYm2", "Actual CFYm2", "Budget CFYm3", "Actual CFYm3"], ["Infrastructure built-up", "Library", "Laboratory equipment", "Staff salary", "Outreach programs", "R&D", "Training / placement / industry", "SDGs", "Entrepreneurship", "Others", "Total amount"]),
        _table("9_8_1", "Table No. 9.8.1: Program-level budget summary", ["Financial Year", "Demanded Budget", "Allocated Budget", "Actual Expenditure", "% Spent", "Students", "Expenditure per Student"], ["CFYm1", "CFYm2", "CFYm3"]),
        _table("9_8_2", "Table No. 9.8.2: Program-level budget and expenditure", ["Item", "Budget CFY", "Actual CFY", "Budget CFYm1", "Actual CFYm1", "Budget CFYm2", "Actual CFYm2", "Budget CFYm3", "Actual CFYm3"], ["Laboratory equipment", "Software", "SDGs", "Faculty development", "R&D", "Industrial training / industry experts / internships", "Miscellaneous", "Total amount"]),
    ],
}
