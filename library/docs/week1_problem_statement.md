# Week 1 - Problem Statement

## 1. PROBLEM STATEMENTS

### I. BOOK BANK - LIBRARY MANAGEMENT SYSTEM

A Library Management System (LMS) is a project that manages and stores books information electronically according to user needs. The system helps students, faculty, and library administrators to keep a constant track of all the books available in the library. It allows both the admin and the member to search for the desired book. It becomes necessary for educational institutes like colleges to keep a continuous check on the books issued and returned and even calculate fines. This task, if carried out manually, will be tedious and includes chances of mistakes. These errors are avoided by allowing the system to keep track of information such as issue date, last date to return the book, and even fine information, and thus there is no need to keep manual track of this information which thereby avoids chances of mistakes. Thus, this system reduces manual work to a great extent and allows smooth flow of library activities by removing chances of errors in the details.

**Existing System:**

The existing system is physical maintenance of the library in which all the library transactions are done manually. This method takes more time for a transaction like borrowing a book or returning a book and also for searching of members and books. Another major disadvantage is that preparing the list of books borrowed and the available books in the library will take more time. It takes several days to verify all records in the case of larger libraries.

**Proposed System:**

The proposed system is a Book Bank / Library Management System (LMS). All the difficulties in manual management of the library have been rectified by implementing a computerized system. With this, the administrator (librarian) can add members, add books, search members, search books, update information, edit information, borrow and return books in quick time.

The proposed system has the following advantages:
1. It provides "better and efficient" service to members.
2. Reduces the workload of employees.
3. Faster retrieval of information about the desired book.
4. Provides facility for proper monitoring, thus reduces paperwork and provides data security.
5. All details will be available at a click.

---

## 2. System Overview for AEC Library

The AEC Library Management System is a web-based application designed to address the problems mentioned above. It provides:

- **Student Portal**: Students can search textbooks and reference books, view availability, request book issues, view their borrowing history, and pay fines online.
- **Admin Portal**: Librarians and administrators can manage book inventory, approve book issues, process returns, calculate and manage fines, and generate reports.
- **Cloud Integration**: Book cover images are stored on Cloudinary CDN for fast access.
- **Payment Integration**: Razorpay gateway for fine payments.
- **Authentication**: Google OAuth 2.0 for secure student login.

---

## 3. Key Features

1. **Book Catalog Management**
   - Add, update, and delete books
   - Categorize books as Textbooks or Reference Books
   - Upload and manage book cover images

2. **Issue and Return Management**
   - Students can request book issues
   - Admin can approve or reject requests
   - Automatic due date calculation (15 days)
   - Return processing with fine calculation

3. **Fine Management**
   - Automatic fine calculation (Rs. 10 per day overdue)
   - Online payment via Razorpay
   - Fine history tracking

4. **Search and Discovery**
   - Search books by title, author, ISBN, or category
   - Real-time availability checking
   - Book recommendations

5. **Reporting and Analytics**
   - Borrowing statistics
   - Fine collection reports
   - Book inventory reports

---

## 4. Technology Stack

- **Backend**: Django 3.1.7 (Python)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Database**: PostgreSQL (Neon)
- **Storage**: Cloudinary (images), Local filesystem (documents)
- **Payments**: Razorpay SDK
- **Deployment**: Render Cloud Platform
- **Authentication**: Google OAuth 2.0

---

## 5. Project Scope

The AEC Library Management System focuses on automating the library operations of Anurag Engineering College. The system replaces manual processes with an efficient digital solution, reducing errors, saving time, and improving the overall library experience for students and staff.
