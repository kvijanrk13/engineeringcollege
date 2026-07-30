# Week 4 - UML Design Models

## AEC Library Management System

The following UML models are reverse-checked against the deployed Django application, its database models, URL routes, Razorpay integration, Cloudinary media delivery, and Render infrastructure. Multiplicities and message names reflect the implementation rather than a generic library example.

## 1. Class Diagram

![Complete AEC Library cross-app class diagram](/static/docs/images/relationships_diagram.svg)

The domain model spans the `library`, `student`, and Django `auth` packages. Its principal associations are:

| Source | Association | Target | Multiplicity |
|---|---|---|---|
| `Author` | author of | `Book` | `1` to `0..*` |
| `Book` | represented by | `Issue` | `1` to `0..*` |
| `Student` | borrower on | `Issue` | `1` to `0..*` |
| `Issue` | has fine records | `Fine` | `1` to `0..*` |
| `Student` | charged through | `Fine` | `1` to `0..*` |
| `Department` | contains | `Student` | `1` to `0..*` |
| `auth.User` | owns profile | `Student` | `1` to `1` |
| `Issue` | updates on save | `LibraryStat` | dependency |

`BookRecommendation` is intentionally independent because it has no foreign-key fields.

### 1.1 Detailed Library Classes

![Detailed Library App class diagram](/static/docs/images/library_class_diagram.svg)

### 1.2 Detailed Student Classes

![Detailed Student App class diagram](/static/docs/images/student_class_diagram.svg)

## 2. Use Case Diagram

![AEC Library use case diagram](/static/docs/images/library_use_case_diagram.svg)

The primary actors are Student and Librarian/Admin. Razorpay is a supporting external actor for fine payment. The diagram covers authentication, catalogue discovery, issue requests, circulation, fine management, and documentation.

## 3. Sequence Diagram

![Book issue return and fine payment sequence diagram](/static/docs/images/library_sequence_diagram.svg)

This interaction traces a complete circulation lifecycle: request creation, librarian approval, issue persistence, return and fine calculation, Razorpay order creation, signature verification, and payment persistence.

## 4. Collaboration Diagram

![AEC Library collaboration diagram](/static/docs/images/library_collaboration_diagram.svg)

The collaboration diagram presents the same runtime behavior as numbered messages between participating objects. It emphasizes object links and responsibility distribution rather than time on a vertical axis.

## 5. Statechart Diagram

![Issue lifecycle statechart diagram](/static/docs/images/library_statechart_diagram.svg)

The state machine models an `Issue` record through Requested, Issued, Overdue, Returned, Fine Outstanding, Closed, and cancellation paths. Guards correspond to `issued`, `returned`, `return_date`, `Fine.amount`, and `Fine.paid`.

## 6. Activity Diagram

![Borrow return and fine processing activity diagram](/static/docs/images/library_activity_diagram.svg)

Swimlanes separate Student, Django System, and Librarian/Payment Gateway responsibilities across login, selection, approval, return, fine calculation, and transaction closure.

## 7. Component Diagram

![AEC Library component diagram](/static/docs/images/library_component_diagram.svg)

The component view shows the browser, Django routing and views, templates, domain models, ORM, fine utility, PostgreSQL, Cloudinary, and Razorpay with their provided dependencies.

## 8. Deployment Diagram

![AEC Library deployment diagram](/static/docs/images/library_deployment_diagram.svg)

The deployment model reflects the production topology: user browser over HTTPS, Gunicorn and Django on the Render web service, Render PostgreSQL through `DATABASE_URL`, and HTTPS integrations with Cloudinary and Razorpay.

## UML Notation

| Notation | Meaning |
|---|---|
| `+` / `-` | Public operation / private attribute |
| `1`, `0..1`, `0..*` | Relationship multiplicity |
| Solid connector | Association, call, or deployed communication path |
| Dashed connector | Dependency, reply, or external integration |
| Open arrowhead | Navigability or message direction |
| Filled initial node / bullseye | Initial state / final state |
