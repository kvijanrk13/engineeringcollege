# Week 4 - Design Structural Models

## 1. DESIGN STRUCTURAL MODELS

### I. AEC LIBRARY MANAGEMENT SYSTEM

The structural models below are reverse-checked against the Django model definitions. Every persistent class is shown with named associations, navigability, and multiplicities at both ends. Dashed connectors identify cross-app references or update dependencies.

#### 1.1 Class Diagram - Library App

![Complete Library App class diagram with explicit relationships](/static/docs/images/library_class_diagram.svg)

**Classes shown:** `Author`, `Book`, `Issue`, `Fine`, `LibraryStat`, and `BookRecommendation`. The external `Student` class is included because `Issue.student` and `Fine.student` are foreign keys into the Student app.

#### 1.2 Class Diagram - Student App

![Complete Student App class diagram with explicit relationships](/static/docs/images/student_class_diagram.svg)

**Classes shown:** `User`, `Student`, and `Department`.

#### 1.3 Relationships Between Apps

![Complete cross-app domain model](/static/docs/images/relationships_diagram.svg)

This combined view shows how the `library`, `student`, and Django `auth` packages form one domain model. `BookRecommendation` has no foreign-key associations; it is intentionally shown as an independent class.

#### 1.4 UML Relationship Summary

| Source | Relationship | Target | Multiplicity |
|---|---|---|---|
| `Author` | writes | `Book` | `1` to `0..*` |
| `Book` | has issue records | `Issue` | `1` to `0..*` |
| `Student` | borrows through | `Issue` | `1` to `0..*` |
| `Issue` | has fine records | `Fine` | `1` to `0..*` |
| `Student` | is charged through | `Fine` | `1` to `0..*` |
| `Department` | contains | `Student` | `1` to `0..*` |
| `User` | owns profile | `Student` | `1` to `1` |
| `Issue` | updates on save | `LibraryStat` | dependency |
| `BookRecommendation` | no association | — | independent |

#### 1.5 UML Notation

| Notation | Meaning |
|---|---|
| `+` | Public operation |
| `-` | Private attribute |
| `1` | Exactly one instance |
| `0..1` | Zero or one instance |
| `0..*` | Zero or many instances |
| Solid line | Association |
| Dashed line | Cross-app reference or update dependency |
| Open arrowhead | Navigability toward the referenced class |

#### 1.6 Model Details

- **Author** stores an author's name and description and is associated with many books.
- **Book** stores catalogue details and belongs to one author.
- **Issue** connects a student and a book and tracks issue and return dates.
- **Fine** belongs to an issue and records the amount and payment status.
- **LibraryStat** stores the current borrowed-book count and is recalculated by the `Issue` post-save signal.
- **BookRecommendation** stores acquisition recommendations independently of the catalogue.
- **Student** links an authenticated user to a department and personal details.
- **Department** groups students by department name.

## 2. DESIGN BEHAVIORAL MODELS

### 2.1 Use Case Diagram - Student

![StarUML-style Student use case diagram](/static/docs/images/student_use_case_diagram.svg)

### 2.2 Use Case Diagram - Librarian/Admin

![StarUML-style Librarian and Admin use case diagram](/static/docs/images/admin_use_case_diagram.svg)

### 2.3 Sequence Diagram - Book Issue Flow

![StarUML-style book issue sequence diagram](/static/docs/images/book_issue_sequence_diagram.svg)

### 2.4 Statechart Diagram - Book Status

![StarUML-style book status state machine diagram](/static/docs/images/book_status_statechart_diagram.svg)

### 2.5 Activity Diagram - Library Operations

![StarUML-style library operations activity diagram](/static/docs/images/library_operations_activity_diagram.svg)
