# EngineeringCollege DBMS Schema and Queries

## Scope

This document contains the DBMS schema notes and sample SQL queries for the EngineeringCollege Department Management System only. The schema focuses on department administration, faculty records, student records, certificates, research publications, FDP/workshop data, B.Tech project guidance, subject assignment, faculty profiles, and audit logs.

## Main Django Model Files

- `Project Source/dashboard/models.py`
- `Project Source/dashboard/forms.py`
- `Project Source/dashboard/views.py`
- `Project Source/dashboard/migrations/`
- `Project Source/engineeringcollege/settings.py`

## Migration Commands

```powershell
cd "Project Source"
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```

## Main Tables

| Django Model | Database Table | Purpose |
|---|---|---|
| `Subject` | `dashboard_subject` | Stores subjects handled by faculty members. |
| `Faculty` | `dashboard_faculty` | Stores faculty personal, contact, professional, educational, document, research-summary, and generated-PDF details. |
| `FacultyProfile` | `dashboard_facultyprofile` | Stores additional one-to-one faculty profile information such as experience and batch number. |
| `Certificate` | `dashboard_certificate` | Stores faculty certificate records and uploaded certificate file references. |
| `FacultyLog` | `dashboard_facultylog` | Stores audit history for important faculty/student operations. |
| `ResearchProject` | `dashboard_researchproject` | Stores faculty research project and publication-like summary records. |
| `ResearchPublication` | `dashboard_researchpublication` | Stores detailed faculty research publications, patents, books, awards, and proof-document references. |
| `StudentResearchPublication` | `dashboard_studentresearchpublication` | Stores student research publication details and proof-document references. |
| `FDP` | `dashboard_fdp` | Stores faculty FDP, workshop, seminar, conference, and training program records. |
| `BTechProject` | `dashboard_btechproject` | Stores B.Tech project guidance records connected to faculty members. |
| `Student` | `dashboard_student` | Stores student personal, academic, certificate, training, research, and generated-PDF details. |
| `Faculty.subjects` | `dashboard_faculty_subjects` | Many-to-many bridge table between faculty and subjects. |

## Entity Descriptions

### Subject

| Field | Type | Description |
|---|---|---|
| `id` | BigAutoField | Primary key. |
| `name` | CharField | Subject name. |
| `code` | CharField | Optional subject code. |
| `credits` | IntegerField | Subject credits. |

### Faculty

| Field Group | Important Fields | Description |
|---|---|---|
| Identity | `staff_name`, `employee_code` | Faculty name and unique employee code. |
| Personal | `father_name`, `mother_name`, `dob`, `gender`, `state`, `caste`, `nationality`, `address` | Personal details. |
| Contact | `mobile`, `phone`, `email` | Communication details. |
| Professional | `department`, `designation`, `joining_date`, `jntuh_id`, `aicte_id`, `pan`, `aadhar`, `apaar_id`, `orcid_id` | Employment and identity information. |
| Education | `ssc_*`, `inter_*`, `ug_*`, `pg_*`, `phd_*` | Qualification details. |
| Academic Work | `subjects_dealt`, `classes_taken`, `results`, `scm`, `about_yourself` | Teaching and academic summary. |
| Documents | `photo`, certificate/document file fields, document URL fields | Uploaded document references. |
| PDF | `pdf_document`, `pdf_password` | Generated faculty profile PDF and optional password. |
| Status | `is_active`, `created_at`, `updated_at` | Record status and timestamps. |

### Student

| Field Group | Important Fields | Description |
|---|---|---|
| Identity | `ht_no`, `student_name` | Student hall-ticket number and name. |
| Personal | `father_name`, `mother_name`, `gender`, `dob`, `age`, `nationality`, `category`, `religion`, `blood_group`, `aadhar`, `apaar_id`, `address` | Personal details. |
| Contact | `parent_phone`, `student_phone`, `email` | Communication details. |
| Academic | `department`, `year`, `sem`, `ssc_*`, `inter_*`, `btech_year`, `ug_college_name`, `cgpa` | Academic details. |
| Memberships | `task_registered`, `task_username`, `csi_registered`, `csi_membership_id` | Student membership information. |
| Training/Projects | `rtrp_project_title`, `intern_title`, `final_project_title`, `other_training` | Student project and training details. |
| Documents | `photo`, certificate file fields, certificate URL fields | Uploaded certificate and image references. |
| PDF | `pdf_file`, `pdf_url`, `pdf_generated`, `pdf_generation_time`, `pdf_password` | Generated student profile PDF details. |
| Timestamps | `created_at`, `updated_at` | Record creation and modification times. |

### Certificate

| Field | Type | Description |
|---|---|---|
| `faculty_id` | ForeignKey | Linked faculty record. |
| `certificate_type` | CharField | Type or title of certificate. |
| `certificate_file` | FileField | Uploaded certificate file. |
| `issued_by` | CharField | Issuing organization. |
| `issue_date` | DateField | Certificate issue date. |
| `description` | TextField | Certificate notes. |
| `uploaded_at` | DateTimeField | Upload timestamp. |

### ResearchPublication

Stores detailed faculty research output. Important fields include `faculty_id`, `research_type`, `title`, `authors`, `department`, `publication_year`, `academic_year`, `status`, `doi`, `url`, `journal_name`, `issn`, `conference_name`, `book_title`, `patent_number`, `project_title`, `funding_agency`, `award_title`, `publisher_name`, `proof_document`, `created_at`, and `updated_at`.

### StudentResearchPublication

Stores student research output. Important fields include `student_id`, `research_type`, `title`, `authors`, `academic_year`, `publication_year`, `journal_name`, `conference_name`, `issn`, `doi`, `url`, `status`, `proof_document`, `created_at`, and `updated_at`.

### FDP

Stores faculty FDP/workshop/seminar/conference/training records. Important fields include `faculty_id`, `fdp_type`, `title`, `from_date`, `to_date`, `academic_year`, `organized_by`, `place`, `mode`, `level`, `role`, `sponsored_by`, `remarks`, `certificate`, and `created_at`.

### BTechProject

Stores student project guidance records. Important fields include `faculty_id`, `ht_no`, `student_name`, `batch`, `project_title`, `approved`, `marks`, and `created_at`.

### FacultyLog

Stores activity history. Important fields include `faculty_id`, `student_id`, `action`, `details`, `performed_by`, `ip_address`, and `created_at`.

## Relationships

| Relationship | Type | Description |
|---|---|---|
| `Faculty` to `FacultyProfile` | One-to-one | Each faculty member can have one extended profile. |
| `Faculty` to `Certificate` | One-to-many | A faculty member can have many certificate records. |
| `Faculty` to `ResearchPublication` | One-to-many | A faculty member can have many research publications. |
| `Faculty` to `FDP` | One-to-many | A faculty member can attend many FDP/workshop programs. |
| `Faculty` to `BTechProject` | One-to-many | A faculty member can guide many B.Tech projects. |
| `Student` to `StudentResearchPublication` | One-to-many | A student can have many research publications. |
| `Faculty` to `Subject` | Many-to-many | Faculty members can handle multiple subjects and a subject can be handled by multiple faculty members. |
| `FacultyLog` to `Faculty` | Many-to-one optional | Logs can be linked to a faculty record. |
| `FacultyLog` to `Student` | Many-to-one optional | Logs can be linked to a student record. |

## Sample SQL Queries

### 1. List all active faculty members

```sql
SELECT
    id,
    staff_name,
    employee_code,
    department,
    designation,
    email,
    mobile
FROM dashboard_faculty
WHERE is_active = TRUE
ORDER BY staff_name ASC;
```

### 2. Search faculty by department

```sql
SELECT
    staff_name,
    employee_code,
    designation,
    email
FROM dashboard_faculty
WHERE department = 'Information Technology'
ORDER BY staff_name ASC;
```

### 3. Count faculty members by designation

```sql
SELECT
    designation,
    COUNT(*) AS faculty_count
FROM dashboard_faculty
WHERE is_active = TRUE
GROUP BY designation
ORDER BY faculty_count DESC;
```

### 4. List faculty with assigned subjects

```sql
SELECT
    f.staff_name,
    f.employee_code,
    s.name AS subject_name,
    s.code AS subject_code,
    s.credits
FROM dashboard_faculty f
JOIN dashboard_faculty_subjects fs
    ON f.id = fs.faculty_id
JOIN dashboard_subject s
    ON s.id = fs.subject_id
ORDER BY f.staff_name, s.name;
```

### 5. List all students by year and semester

```sql
SELECT
    ht_no,
    student_name,
    department,
    year,
    sem,
    email,
    student_phone
FROM dashboard_student
ORDER BY year ASC, sem ASC, ht_no ASC;
```

### 6. Search a student by hall-ticket number

```sql
SELECT
    id,
    ht_no,
    student_name,
    department,
    year,
    sem,
    cgpa
FROM dashboard_student
WHERE ht_no = '23C11A1201';
```

### 7. Count students by academic year

```sql
SELECT
    year,
    COUNT(*) AS student_count
FROM dashboard_student
GROUP BY year
ORDER BY year ASC;
```

### 8. List generated student PDFs

```sql
SELECT
    ht_no,
    student_name,
    pdf_generated,
    pdf_generation_time,
    pdf_file
FROM dashboard_student
WHERE pdf_generated = TRUE
ORDER BY pdf_generation_time DESC;
```

### 9. List faculty certificate records

```sql
SELECT
    f.staff_name,
    f.employee_code,
    c.certificate_type,
    c.issued_by,
    c.issue_date,
    c.uploaded_at
FROM dashboard_certificate c
JOIN dashboard_faculty f
    ON f.id = c.faculty_id
ORDER BY c.uploaded_at DESC;
```

### 10. List faculty research publications

```sql
SELECT
    f.staff_name,
    f.employee_code,
    r.research_type,
    r.title,
    r.publication_year,
    r.status,
    r.journal_name,
    r.doi
FROM dashboard_researchpublication r
JOIN dashboard_faculty f
    ON f.id = r.faculty_id
ORDER BY r.publication_year DESC, f.staff_name ASC;
```

### 11. Count faculty research publications by year

```sql
SELECT
    publication_year,
    COUNT(*) AS publication_count
FROM dashboard_researchpublication
WHERE publication_year IS NOT NULL
GROUP BY publication_year
ORDER BY publication_year DESC;
```

### 12. List student research publications

```sql
SELECT
    s.ht_no,
    s.student_name,
    sr.title,
    sr.research_type,
    sr.publication_year,
    sr.status
FROM dashboard_studentresearchpublication sr
JOIN dashboard_student s
    ON s.id = sr.student_id
ORDER BY sr.publication_year DESC, s.ht_no ASC;
```

### 13. List FDP/workshop records for faculty

```sql
SELECT
    f.staff_name,
    f.employee_code,
    fd.fdp_type,
    fd.title,
    fd.from_date,
    fd.to_date,
    fd.mode,
    fd.level,
    fd.role
FROM dashboard_fdp fd
JOIN dashboard_faculty f
    ON f.id = fd.faculty_id
ORDER BY fd.from_date DESC;
```

### 14. Calculate FDP duration in days

```sql
SELECT
    f.staff_name,
    fd.title,
    fd.from_date,
    fd.to_date,
    (fd.to_date - fd.from_date + 1) AS duration_days
FROM dashboard_fdp fd
JOIN dashboard_faculty f
    ON f.id = fd.faculty_id
ORDER BY fd.from_date DESC;
```

### 15. List B.Tech projects guided by faculty

```sql
SELECT
    f.staff_name AS guide_name,
    f.employee_code,
    bp.ht_no,
    bp.student_name,
    bp.batch,
    bp.project_title,
    bp.approved,
    bp.marks
FROM dashboard_btechproject bp
JOIN dashboard_faculty f
    ON f.id = bp.faculty_id
ORDER BY bp.batch DESC, f.staff_name ASC;
```

### 16. Count approved B.Tech projects by faculty

```sql
SELECT
    f.staff_name,
    f.employee_code,
    COUNT(bp.id) AS approved_project_count
FROM dashboard_faculty f
LEFT JOIN dashboard_btechproject bp
    ON f.id = bp.faculty_id
   AND bp.approved = TRUE
GROUP BY f.id, f.staff_name, f.employee_code
ORDER BY approved_project_count DESC;
```

### 17. View recent activity logs

```sql
SELECT
    action,
    details,
    performed_by,
    ip_address,
    created_at
FROM dashboard_facultylog
ORDER BY created_at DESC
LIMIT 25;
```

### 18. Find faculty records missing email

```sql
SELECT
    staff_name,
    employee_code,
    department,
    designation
FROM dashboard_faculty
WHERE email IS NULL OR email = ''
ORDER BY staff_name ASC;
```

### 19. Find student records missing phone number

```sql
SELECT
    ht_no,
    student_name,
    department,
    year,
    sem
FROM dashboard_student
WHERE student_phone IS NULL OR student_phone = ''
ORDER BY ht_no ASC;
```

### 20. Dashboard summary counts

```sql
SELECT
    (SELECT COUNT(*) FROM dashboard_faculty WHERE is_active = TRUE) AS active_faculty,
    (SELECT COUNT(*) FROM dashboard_student) AS total_students,
    (SELECT COUNT(*) FROM dashboard_certificate) AS total_certificates,
    (SELECT COUNT(*) FROM dashboard_researchpublication) AS faculty_publications,
    (SELECT COUNT(*) FROM dashboard_fdp) AS fdp_records,
    (SELECT COUNT(*) FROM dashboard_btechproject) AS btech_projects;
```

## Backup and Restore Notes

For SQLite local development, copy `db.sqlite3` after stopping the server:

```powershell
Copy-Item .\db.sqlite3 .\backup\db.sqlite3
```

For PostgreSQL, use standard export and restore tools:

```powershell
pg_dump "<database-url>" > engineeringcollege_backup.sql
psql "<database-url>" < engineeringcollege_backup.sql
```

## Data Safety Notes

- Do not commit real student or faculty personal data into the project repository.
- Do not store database passwords or private connection URLs in documentation.
- Keep backups encrypted when they contain academic or personal records.
- Use sample or anonymized values in project reports and demonstrations.
