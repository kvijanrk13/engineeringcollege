# Week 1 - Problem Statement

## AEC Library Management System

The library needs a simple online system to replace manual book searching, issue registers, return tracking,
and fine calculation. Students should be able to find books, request issues, view due dates, and pay fines.
Librarians should be able to manage books, approve requests, record returns, and control fines.

## Objectives

- Provide secure Student and Librarian login.
- Maintain Authors, Books, Students, Issues, and Fines.
- Support search, issue request, approval, return, and payment.
- Calculate overdue fines automatically at ₹10 per day.
- Provide accurate availability and circulation information.

## Users

| User | Main activities |
|---|---|
| Student | Login, search books, request books, view issues/fines, pay fines |
| Librarian/Admin | Manage books, approve issues, process returns, manage fines |

## Expected Outcome

A responsive Django web application with PostgreSQL storage, Cloudinary media, Razorpay payment support,
role-based access, and online documentation.
