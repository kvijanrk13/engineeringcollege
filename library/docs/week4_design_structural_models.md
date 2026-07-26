# Week 4 - Design Structural Models

## 1. DESIGN STRUCTURAL MODELS

### I. AEC LIBRARY MANAGEMENT SYSTEM

#### 1.1 Class Diagram - Library App

```
┌─────────────────────────────────────────────────────────────────┐
│                          Author                                 │
├─────────────────────────────────────────────────────────────────┤
│ - id : BigInteger                                               │
│ - name : Varchar(350)                                           │
│ - description : Varchar(450)                                    │
├─────────────────────────────────────────────────────────────────┤
│ + __str__() : String                                            │
└─────────────────────────────────────────────────────────────────┘
                              ▲ 1
                              │
                              │
┌─────────────────────────────────────────────────────────────────┐
│                            Book                                  │
├─────────────────────────────────────────────────────────────────┤
│ - id : BigInteger                                               │
│ - name : Varchar(350)                                           │
│ - image : ImageField                                            │
│ - category : Varchar(220)                                       │
├─────────────────────────────────────────────────────────────────┤
│ + __str__() : String                                            │
│ + cloudinary_image_url() : String                               │
└─────────────────────────────────────────────────────────────────┘
                              │ 1
                              │
                              │
┌─────────────────────────────────────────────────────────────────┐
│                            Issue                                 │
├─────────────────────────────────────────────────────────────────┤
│ - id : BigInteger                                               │
│ - created_at : DateTime                                         │
│ - issued : Boolean                                              │
│ - issued_at : DateTime (nullable)                               │
│ - returned : Boolean                                            │
│ - return_date : DateTime (nullable)                             │
├─────────────────────────────────────────────────────────────────┤
│ + __str__() : String                                            │
│ + days_no() : String                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                             Fine                                 │
├─────────────────────────────────────────────────────────────────┤
│ - id : BigInteger                                               │
│ - amount : Decimal(10,2)                                        │
│ - paid : Boolean                                                │
│ - order_id : Varchar(500) [unique]                              │
│ - datetime_of_payment : DateTime (nullable)                     │
│ - razorpay_order_id : Varchar(500) (nullable)                   │
│ - razorpay_payment_id : Varchar(500) (nullable)                 │
│ - razorpay_signature : Varchar(500) (nullable)                  │
├─────────────────────────────────────────────────────────────────┤
│ + save()                                                       │
│ + __str__() : String                                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        LibraryStat                               │
├─────────────────────────────────────────────────────────────────┤
│ - id : BigInteger                                               │
│ - borrowed_books : PositiveInteger                              │
├─────────────────────────────────────────────────────────────────┤
│ + __str__() : String                                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     BookRecommendation                           │
├─────────────────────────────────────────────────────────────────┤
│ - id : BigInteger                                               │
│ - image : ImageField (nullable)                                 │
│ - title : Varchar(350) (blank)                                  │
│ - author : Varchar(350) (blank)                                 │
│ - book_type : TextField (blank)                                 │
│ - isbn : Varchar(50) (blank)                                    │
│ - publisher : Varchar(200) (blank)                              │
│ - edition_year : Varchar(50) (blank)                            │
│ - book_format : Varchar(10) (blank)                             │
│ - copies_recommended : Varchar(20) (blank)                      │
│ - existing : Varchar(20) (blank)                                │
│ - cost : Varchar(50) (blank)                                    │
│ - created_at : DateTime                                         │
├─────────────────────────────────────────────────────────────────┤
│ + __str__() : String                                            │
└─────────────────────────────────────────────────────────────────┘
```

#### 1.2 Class Diagram - Student App

```
┌─────────────────────────────────────────────────────────────────┐
│                          Department                             │
├─────────────────────────────────────────────────────────────────┤
│ - id : BigInteger                                               │
│ - name : Varchar(200)                                           │
├─────────────────────────────────────────────────────────────────┤
│ + __str__() : String                                            │
└─────────────────────────────────────────────────────────────────┘
                              ▲ 1
                              │
                              │
┌─────────────────────────────────────────────────────────────────┐
│                           Student                                │
├─────────────────────────────────────────────────────────────────┤
│ - id : BigInteger                                               │
│ - first_name : Varchar(120)                                     │
│ - last_name : Varchar(120)                                      │
├─────────────────────────────────────────────────────────────────┤
│ + __str__() : String                                            │
└─────────────────────────────────────────────────────────────────┘
                              │ 1
                              │
                              │
┌─────────────────────────────────────────────────────────────────┐
│               auth_user (Django Built-in)                        │
├─────────────────────────────────────────────────────────────────┤
│ - id : BigInteger                                               │
│ - username : Varchar(150) [unique]                              │
│ - password : Varchar(128)                                       │
│ - email : Varchar(254)                                          │
│ - is_active : Boolean                                           │
│ - is_staff : Boolean                                            │
│ - is_superuser : Boolean                                        │
│ - last_login : DateTime (nullable)                              │
│ - date_joined : DateTime                                        │
├─────────────────────────────────────────────────────────────────┤
│ + __str__() : String                                            │
└─────────────────────────────────────────────────────────────────┘
```

#### 1.3 Relationships Between Apps

```
┌─────────────────────────────────────────────────────────────────┐
│                        Library App                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │   Author   │  │    Book    │  │   Issue    │               │
│  └────────────┘  └────────────┘  └────────────┘               │
│       ▲ 1             │ 1              │ 1                     │
│       │               │               │                       │
│       └───────────────┴───────────────┘                       │
│                         │                                       │
│                         ▼                                       │
│                  ┌────────────┐                                 │
│                  │    Fine    │                                 │
│                  └────────────┘                                 │
│                         │                                       │
│                         │ 1                                     │
│                         ▼                                       │
│  ┌────────────┐  ┌────────────────┐  ┌────────────┐           │
│  │  Student   │◄─┤     Issue      │─►│    Book    │           │
│  │ (Foreign)  │  │ (Student FK)   │  │ (Book FK)  │           │
│  └────────────┘  └────────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Student App                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐           │
│  │ Department │  │  Student   │  │  auth_user      │           │
│  └────────────┘  └────────────┘  └────────────────┘           │
│       ▲ 1             │ 1              │ 1                     │
│       │               │               │                       │
│       └───────────────┴───────────────┘                       │
│                         │                                       │
│                         ▼                                       │
│                  Student.student_id                            │
│              (OneToOne → auth_user.id)                          │
└─────────────────────────────────────────────────────────────────┘
```

#### 1.4 STAR UML Notation Summary

| Symbol | Meaning |
|--------|---------|
| `▲` | Inheritance/Parent class |
| `│` | Association relationship |
| `1` | Exactly one |
| `*` | Zero or many |
| `0..1` | Zero or one |
| `1..*` | One or many |

**Relationships:**
- `Author 1 ──── * Book` : One author can write many books
- `Book 1 ──── * Issue` : One book can have many issue records
- `Student 1 ──── * Issue` : One student can have many issue records
- `Issue 1 ──── 1 Fine` : One issue can have one fine
- `Department 1 ──── * Student` : One department has many students
- `User 1 ──── 1 Student` : One user account linked to one student profile

#### 1.5 Model Details

**Author Model:**
- Primary Key: `id` (Auto-increment)
- Attributes: `name` (350 chars), `description` (450 chars)
- Relationships: One-to-Many with Book

**Book Model:**
- Primary Key: `id` (Auto-increment)
- Foreign Key: `author` → Author
- Attributes: `name` (350 chars), `image` (ImageField), `category` (220 chars)
- Relationships: Many-to-One with Author, One-to-Many with Issue

**Issue Model:**
- Primary Key: `id` (Auto-increment)
- Foreign Keys: `student` → Student, `book` → Book
- Attributes: `created_at`, `issued` (Boolean), `issued_at`, `returned` (Boolean), `return_date`
- Relationships: Many-to-One with Student and Book, One-to-One with Fine

**Fine Model:**
- Primary Key: `id` (Auto-increment)
- Foreign Keys: `student` → Student, `issue` → Issue
- Attributes: `amount` (Decimal), `paid` (Boolean), `order_id` (unique), payment fields
- Relationships: Many-to-One with Student and Issue

**LibraryStat Model:**
- Primary Key: `id` (Auto-increment)
- Attributes: `borrowed_books` (PositiveInteger)
- Purpose: Singleton-like stats tracking currently borrowed books

**Student Model:**
- Primary Key: `id` (Auto-increment)
- Foreign Key: `department` → Department
- OneToOne: `student_id` → auth_user.id
- Attributes: `first_name` (120 chars), `last_name` (120 chars)

**Department Model:**
- Primary Key: `id` (Auto-increment)
- Attributes: `name` (200 chars)
- Relationships: One-to-Many with Student

---

## 2. DESIGN BEHAVIORAL MODELS

### 2.1 Use Case Diagram - Student

```
┌─────────────────────────────────────────────────────────────────┐
│                         Student                                 │
├─────────────────────────────────────────────────────────────────┤
│  Use Cases:                                                     │
│  - Login using Google Gmail                                     │
│  - Search books by Title, Author, ISBN, Category               │
│  - View book availability                                       │
│  - Request book issue                                           │
│  - View borrowing history                                       │
│  - View fine details                                            │
│  - Pay fine online                                              │
│  - Update personal profile                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Use Case Diagram - Librarian/Admin

```
┌─────────────────────────────────────────────────────────────────┐
│                      Librarian / Admin                          │
├─────────────────────────────────────────────────────────────────┤
│  Use Cases:                                                     │
│  - Secure login                                                 │
│  - Add new books                                                │
│  - Update book details                                          │
│  - Delete books                                                 │
│  - Manage student records                                       │
│  - Issue books                                                  │
│  - Return books                                                 │
│  - Renew books                                                  │
│  - Calculate fine automatically                                 │
│  - Search books                                                 │
│  - Generate reports                                             │
│  - Manage librarians                                            │
│  - Manage departments                                           │
│  - Manage book categories                                       │
│  - Manage publishers                                            │
│  - Dashboard monitoring                                         │
│  - User management                                              │
│  - Database backup                                              │
│  - System configuration                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Sequence Diagram - Book Issue Flow

```
Student          Librarian          System           Database
   │                │                │                │
   │──Login────────▶│                │                │
   │                │──Validate─────▶│                │
   │                │                │──Query────────▶│
   │                │                │◀─User Data─────│
   │◀─Session───────│                │                │
   │                │                │                │
   │──Search Books──────────────────▶│                │
   │                │                │──Query────────▶│
   │                │                │◀─Book List─────│
   │◀─Results───────│                │                │
   │                │                │                │
   │──Request Issue──────────────────▶│                │
   │                │                │──Create───────▶│
   │                │                │◀─Issue Record──│
   │◀─Confirmation──│                │                │
   │                │                │                │
   │                │──Approve Issue──────────────────▶│
   │                │                │──Update───────▶│
   │                │                │◀─Updated───────│
   │◀─Issued Book───│                │                │
```

### 2.4 Statechart Diagram - Book Status

```
┌─────────────┐
│   Available  │
└──────┬───────┘
       │ Issue Request
       ▼
┌─────────────┐
│  Pending    │──────────────────┐
└──────┬───────┘                  │
       │ Approve                  │ Reject
       ▼                          │
┌─────────────┐                   │
│   Issued     │                   │
└──────┬───────┘                   │
       │ Return                    │
       ▼                           │
┌─────────────┐◄──────────────────┘
│   Returned   │
└─────────────┘
       │
       │ Overdue
       ▼
┌─────────────┐
│   Fine Due   │
└──────┬───────┘
       │ Payment
       ▼
┌─────────────┐
│ Fine Paid    │
└─────────────┘
```

### 2.5 Activity Diagram - Library Operations

```
┌─────────────────────────────────────────────────────────────────┐
│                        Library Operations                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Start                                                          │
│    │                                                            │
│    ├─── Student Actions ───┐                                    │
│    │                        │                                    │
│    │   ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│    │   │  Login   │───▶│ Search   │───▶│ Request  │           │
│    │   └──────────┘    └──────────┘    │  Issue   │           │
│    │                                    └────┬─────┘           │
│    │                                         │                  │
│    │   ┌──────────┐    ┌──────────┐    ┌────┴─────┐           │
│    │   │ View My  │◄───│ Pay Fine │◄───│  My Fines │           │
│    │   │  Issues  │    └──────────┘    └──────────┘           │
│    │   └──────────┘                                            │
│    │                                                           │
│    ├─── Admin Actions ─────┐                                    │
│    │                        │                                    │
│    │   ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│    │   │  Login   │───▶│  View    │───▶│  Issue   │           │
│    │   │          │    │  All     │    │  Book    │           │
│    │   └──────────┘    │ Requests │    └────┬─────┘           │
│    │                    └──────────┘         │                  │
│    │                                      ┌────┴─────┐           │
│    │                    ┌──────────┐    ┌──────────┐           │
│    │                    │  View    │◄───│  Return  │           │
│    │                    │  All     │    │  Book    │           │
│    │                    │  Fines   │    └──────────┘           │
│    │                    └──────────┘                            │
│    │                                                           │
│    └───────────────────────────────────────────────────────────┘
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
