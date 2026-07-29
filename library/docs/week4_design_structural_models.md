# Week 4 - Design Structural Models

## 1. DESIGN STRUCTURAL MODELS

### I. AEC LIBRARY MANAGEMENT SYSTEM

These diagrams use the same visual conventions as a StarUML class diagram: a clean white canvas, rectangular class elements, separate name/attribute/operation compartments, UML visibility markers, named associations, and relationship multiplicities.

#### 1.1 Class Diagram - Library App

![StarUML-style Library App class diagram](/static/docs/images/library_class_diagram.svg)

**Classes shown:** `Author`, `Book`, `Issue`, `Fine`, and `LibraryStat`.

#### 1.2 Class Diagram - Student App

![StarUML-style Student App class diagram](/static/docs/images/student_class_diagram.svg)

**Classes shown:** `User`, `Student`, and `Department`.

#### 1.3 Relationships Between Apps

![StarUML-style relationships between Library and Student apps](/static/docs/images/relationships_diagram.svg)

#### 1.4 UML Relationship Summary

| Source | Relationship | Target | Multiplicity |
|---|---|---|---|
| `Author` | writes | `Book` | `1` to `0..*` |
| `Book` | has issue records | `Issue` | `1` to `0..*` |
| `Student` | borrows through | `Issue` | `1` to `0..*` |
| `Issue` | generates | `Fine` | `1` to `0..1` |
| `Department` | contains | `Student` | `1` to `0..*` |
| `User` | owns profile | `Student` | `1` to `1` |

#### 1.5 UML Notation

| Notation | Meaning |
|---|---|
| `+` | Public operation |
| `-` | Private attribute |
| `1` | Exactly one instance |
| `0..1` | Zero or one instance |
| `0..*` | Zero or many instances |
| Solid line | Association |

#### 1.6 Model Details

- **Author** stores an author's name and description and is associated with many books.
- **Book** stores catalogue details and belongs to one author.
- **Issue** connects a student and a book and tracks issue and return dates.
- **Fine** belongs to an issue and records the amount and payment status.
- **LibraryStat** stores the current borrowed-book count.
- **Student** links an authenticated user to a department and personal details.
- **Department** groups students by department name.
