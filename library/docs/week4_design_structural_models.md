# Week 4 and Week 5 - UML Design Models

## AEC Library Management System

The following UML models are reverse-checked against the deployed Django application, its database models, URL routes, Razorpay integration, Cloudinary media delivery, and Render infrastructure. Multiplicities and message names reflect the implementation rather than a generic library example.

The class diagrams use **arrowless solid associations** for Django `ForeignKey` and `OneToOneField` relationships. Hollow triangular arrowheads are not used because they mean generalization/inheritance in UML, and none of these model relationships is inheritance. The only dashed connector is the `Issue` post-save signal dependency on `LibraryStat`.

## 1. Class Diagram

![Library management system class diagram](/static/docs/images/library_management_class_diagram.svg)

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
| Arrowless solid line in class diagrams | Model association (`ForeignKey` or `OneToOneField`) |
| Dashed connector | Dependency, reply, or external integration |
| Open arrowhead in behavioral diagrams | Message or transition direction |
| Filled initial node / bullseye | Initial state / final state |

## Detailed StarUML Drawing Procedure

### A. Common Project Setup

1. Open StarUML and select **File → New**.
2. In **Model Explorer**, rename the root model to `AEC Library Management System`.
3. Right-click the root model and create three packages with **Add → Package**:
   `library`, `student`, and `external services`.
4. To add any diagram, first select the root model or the package that should own it. Then use
   **Model → Add Diagram → [Diagram Type]**.
5. Rename every diagram immediately in Model Explorer. Use the names shown in the sections below.
6. Keep the **Toolbox**, **Model Explorer**, and **Property Editor** visible. Double-clicking an element,
   or selecting it and pressing `Enter`, opens QuickEdit.
7. Use a white diagram background, black connectors, and one font family throughout. Place elements on
   a grid and leave enough space for connector labels.
8. Use **Format → Show Type**, **Format → Show Visibility**, **Format → Show Multiplicity**, and
   **Format → Show Operation Signature** where applicable.
9. Save the project as `AEC_Library_UML.mdj` before drawing. Save again after completing each diagram.
10. After drawing, inspect every connector at 100% and 150% zoom. No connector should cross through a
    class, actor, state, component, or label.

### B. Class Diagram — `AEC Library Complete Class Diagram`

#### Step 1: Create the diagram and classes

1. Select the root model and choose **Model → Add Diagram → Class Diagram**.
2. Rename it `AEC Library Complete Class Diagram`.
3. Select **Class** in the Toolbox and draw these classes:
   `Author`, `Book`, `Issue`, `Fine`, `BookRecommendation`, `LibraryStat`, `Department`, `Student`,
   and `auth.User`.
4. Arrange `Author → Book → Issue → Fine` across the top.
5. Place `Department → Student → auth.User` across the lower-right area.
6. Place `LibraryStat` below `Issue` and `BookRecommendation` at the lower-left with no association.

#### Step 2: Enter attributes and operations

1. Select each class and press `Ctrl+Enter` to add attributes.
2. Enter attributes using `- name : Type` notation.
3. For `Author`, add `id : BigInteger`, `name : String`, and `description : String`.
4. For `Book`, add `id`, `name`, `image`, `category`, and `author_id : FK`.
5. For `Issue`, add `id`, `book_id : FK`, `student_id : FK`, `created_at`, `issued`, `issued_at`,
   `returned`, and `return_date`.
6. For `Fine`, add `id`, `issue_id : FK`, `student_id : FK`, `amount`, `paid`, `order_id`,
   `datetime_of_payment`, and the three Razorpay identifier/signature fields.
7. For `Student`, add `id`, `department_id : FK`, `student_id_id : OneToOne`, `first_name`, and
   `last_name`.
8. Add the remaining attributes exactly as shown in the rendered diagram.
9. Press `Ctrl+Shift+Enter` to add operations such as `__str__() : String`, `days_no() : String`,
   `save() : void`, and `get_full_name() : String`.

#### Step 3: Draw correct model associations

1. Select **Association**, not Generalization, Aggregation, or Composition.
2. Drag from `Author` to `Book`. Name it `author / books`.
3. Double-click the `Author` end and set multiplicity to `1`.
4. Double-click the `Book` end and set multiplicity to `0..*`.
5. Draw `Book — Issue`, name it `book / issues`, and set `Book = 1`, `Issue = 0..*`.
6. Draw `Issue — Fine`, name it `issue / fines`, and set `Issue = 1`, `Fine = 0..*`.
7. Draw `Student — Issue`, name it `borrower / issues`, and set `Student = 1`, `Issue = 0..*`.
8. Draw `Student — Fine`, name it `student / fines`, and set `Student = 1`, `Fine = 0..*`.
9. Draw `Department — Student`, name it `department / students`, and set
   `Department = 1`, `Student = 0..*`.
10. Draw `auth.User — Student`, name it `account / profile`, and set both ends to `1`.
11. Keep the associations arrowless. A hollow triangle means inheritance and must not be used here.
12. Select **Dependency** and drag from `Issue` to `LibraryStat`. Name it
    `«signal» updates count`.
13. Add a Note beside `BookRecommendation`: `Independent class — no model associations`.
14. Use **Format → Show Multiplicity** if endpoint values are hidden.

#### Step 4: Final class-diagram validation

1. Confirm that every `ForeignKey` has a solid association.
2. Confirm that `student_id` is represented by a `1` to `1` association with `auth.User`.
3. Confirm that `Issue — Fine` is `1` to `0..*`; the Django model does not enforce one fine per issue.
4. Confirm that only the signal dependency is dashed.
5. Move labels so that no class border, attribute, or multiplicity is covered.

### C. Use Case Diagram — `AEC Library Use Cases`

1. Select the root model and add a **Use Case Diagram**.
2. Draw a **Use Case Subject** and name it `AEC Library Management System`.
3. Place `Student` and `Librarian / Admin` actors on the left outside the subject.
4. Place the external `Razorpay` actor on the right outside the subject.
5. Inside the subject, add these Student use cases:
   `Sign up / Login`, `Browse & search books`, `Request / borrow book`,
   `View issue history`, `View fines`, and `Pay fine`.
6. Add these Librarian/Admin use cases:
   `Manage catalogue`, `Review issue requests`, `Issue / return book`,
   `Manage fines`, `Reset circulation`, and `View documentation`.
7. Select **Association** and connect `Student` to each Student use case.
8. Connect `Librarian / Admin` to each administrative use case.
9. Connect `Razorpay` to `Pay fine` and name the association `payment API`.
10. Keep actors outside the system boundary and all use cases inside it.
11. Use **Include** only when one use case always executes another. Use **Extend** only for optional
    behavior. Do not use either merely to reduce line count.
12. Align use cases in two clean rows and ensure actor associations do not cross use-case ellipses.

### D. Sequence Diagram — `Book Issue Return and Fine Payment`

1. Add a **Sequence Diagram** under the root model.
2. From left to right, add Lifelines named:
   `student:Student`, `ui:BrowserUI`, `views:LibraryViews`, `orm:ModelsORM`,
   `db:PostgreSQL`, `admin:Librarian`, and `payment:Razorpay`.
3. Keep equal horizontal spacing and extend all lifelines to the same lower boundary.
4. Add synchronous messages in this order:
   `requestBook(bookID)`, `issuerequest(bookID)`, `get_or_create(Issue)`, and `INSERT / SELECT`.
5. Add dashed Reply Messages for `issue record` and `request confirmed`.
6. From `admin:Librarian`, add `approveIssue(issueID)` to `views:LibraryViews`.
7. Add `set issued_at and return_date` to the ORM, followed by `UPDATE Issue` to PostgreSQL.
8. Add `returnBook(issueID)` from Librarian to Views.
9. Add `calcFine(issue)` and `mark returned` from Views to the ORM.
10. Add the resulting `UPDATE Issue / Fine` database message.
11. Add the payment messages:
    `payFine(fineID)`, `createOrder()`, `order details`, `verifySignature()`, and `mark Fine paid`.
12. Add execution specifications on `LibraryViews`, `ModelsORM`, and `Razorpay` while they process calls.
13. Set the diagram property `showSequenceNumber = true`, or type custom numbers if required.
14. Use solid arrows for calls and dashed arrows for replies. Time must progress strictly downward.

### E. Collaboration/Communication Diagram — `AEC Library Collaboration`

1. Add a **Communication Diagram**. StarUML uses “Communication Diagram” for the UML collaboration view.
2. Add Lifelines or object roles named:
   `student:Student`, `ui:Browser`, `views:LibraryViews`, `admin:Librarian`,
   `orm:DjangoORM`, `db:PostgreSQL`, `fine:Fine`, and `razorpay:Gateway`.
3. Arrange the objects around an open center so connector labels remain visible.
4. Use **Connector** to link only objects that directly exchange messages.
5. Add a Forward Message by selecting **Forward Message** and clicking the appropriate connector.
6. Add messages with hierarchical numbering:
   `1: requestBook(bookID)`,
   `1.1: issuerequest()`,
   `1.2: create Issue`,
   `1.3: SQL INSERT`,
   `2: review / approve`,
   `2.1: update Issue`,
   `3: returnBook(issueID)`,
   `3.1: calcFine()`,
   `4: checkout / callback`,
   `4.1: createOrder()`,
   `4.2: order response`,
   `4.3: verifySignature()`,
   and `4.4: mark Fine paid`.
7. Enable `showSequenceNumber` in the diagram Property Editor.
8. If entering numbers manually, set `sequenceNumbering` to `custom`.
9. Confirm that the same scenario and ordering are represented in both Sequence and Communication diagrams.
10. Reposition message labels so they do not overlap object rectangles or other connectors.

### F. Statechart Diagram — `Issue Lifecycle`

1. Add a **Statechart Diagram**.
2. Place an **Initial State** at the far left.
3. Add Simple States named `Requested`, `Issued`, `Overdue`, `Returned`,
   `Fine Outstanding`, and `Closed`.
4. Add an **Activity Final** state after `Closed`.
5. Draw a Transition from Initial to `Requested` and label it `request`.
6. Draw `Requested → Issued` with `approve / issue`.
7. Draw `Issued → Overdue` with `due date passes [now > return_date]`.
8. Draw `Issued → Returned` with `return [on time]`.
9. Draw `Overdue → Returned` with `return / calculate fine`.
10. Draw `Returned → Fine Outstanding` with guard `[amount > 0]`.
11. Draw `Returned → Closed` with guard `[amount = 0]`.
12. Draw `Fine Outstanding → Closed` with `pay or waive`.
13. Draw `Closed → Activity Final` with `complete`.
14. Add an optional cancellation transition from `Requested` to `Closed` named
    `cancel / clear pending`.
15. Put event names before `/`, guards inside `[ ]`, and effects after `/`.
16. Verify that every non-final state has a valid outgoing path.

### G. Activity Diagram — `Borrow Return and Fine Processing`

1. Add an **Activity Diagram**.
2. Draw three vertical Swimlanes named `Student`, `Django System`, and
   `Librarian / Payment Gateway`.
3. Put an **Initial Node** at the top of the Student lane.
4. Add Student actions: `Login`, `Search / select book`, `Request issue`, and `Return book`.
5. Add Django actions: `Authenticate user`, `Create Issue request`,
   `Set 15-day return date`, `Calculate fine`, and `Close transaction`.
6. Add external/admin actions: `Review request`, `Approve and issue`, and `Pay / waive fine`.
7. Connect the actions with **Control Flow** in execution order.
8. Place a Decision Node after `Calculate fine` and name the outgoing guards `[fine > 0]`
   and `[no fine]`.
9. Route `[fine > 0]` to `Pay / waive fine`, then to `Close transaction`.
10. Route `[no fine]` directly to `Close transaction`.
11. Add an **Activity Final Node** below `Close transaction`.
12. Ensure every action is placed in the lane of the party responsible for performing it.
13. Avoid backward-flow lines where possible; the primary activity direction should be top to bottom.

### H. Component Diagram — `AEC Library Components`

1. Add a **Component Diagram**.
2. Add components named `Browser UI`, `Django URL Router`, `Library Views`,
   `Student/Auth Views`, `Templates & Static SVGs`, `Domain Models / ORM`,
   and `Fine Utility`.
3. Add external/database components named `PostgreSQL`, `Cloudinary`, and `Razorpay API`.
4. Arrange Browser on the left, Django application components in the center, and external services on the right.
5. Use **Dependency** from `Browser UI` to `Django URL Router`; label it `HTTPS`.
6. Connect Router to both view components and label the dependencies `dispatch` and `auth routes`.
7. Connect Library Views to Templates and Domain Models with `render` and `query`.
8. Connect Student/Auth Views to Domain Models with `user profile`.
9. Connect Domain Models/ORM to PostgreSQL with `SQL`.
10. Connect Models to Cloudinary with `image URLs`.
11. Connect Library Views to Fine Utility with `calcFine()`.
12. Connect Library Views to Razorpay with `orders / signatures`.
13. Use dashed Dependency arrows for “uses” relationships. Use provided/required interfaces only if
    you want to expose explicit service contracts.
14. Confirm that no database or external API is drawn as an internal Django module.

### I. Deployment Diagram — `AEC Library Deployment`

1. Add a **Deployment Diagram**.
2. Add a Node named `Student / Librarian Device` with stereotype `«device»`.
3. Place an Artifact or deployed component named `Web Browser` inside it.
4. Add a large Node named `Render Web Service: anrkitdept` with stereotype
   `«execution environment»`.
5. Inside the Render node, place `Gunicorn`, `Django Application`,
   `Templates / Static Files`, `Library + Student Apps`, and `Django ORM`.
6. Add a Node named `Render PostgreSQL` with stereotype `«database node»`.
7. Place the database artifact `anrkitdept-db` inside the PostgreSQL node.
8. Add a Node named `External Cloud Services` with stereotype `«cloud»`.
9. Place `Cloudinary` and `Razorpay` service components inside the cloud node.
10. Select **Communication Path** and connect Device to Render Web Service. Label it `HTTPS`.
11. Connect Render Web Service to Render PostgreSQL and label it `TLS / DATABASE_URL`.
12. Connect Render Web Service to Cloudinary with `HTTPS media`.
13. Connect Render Web Service to Razorpay with `HTTPS payment API`.
14. Inside the web node, show `Gunicorn → Django Application` as `WSGI`.
15. Show Django Application loading the apps/templates and the apps using Django ORM.
16. Add a Note containing:
    `Build: build.sh → collectstatic + migrate`,
    `Runtime: gunicorn engineeringcollege.wsgi:application`,
    and `Secrets: Render environment variables`.
17. Verify that physical/runtime nodes contain deployable artifacts and that communication paths
    connect nodes rather than ordinary classes.

### J. Formatting, Review, and Export

1. Select related elements and use **Format → Align** and **Format → Distribute** for consistent spacing.
2. Increase the default font until labels remain readable when the diagram is fitted to one page.
3. Keep relationship labels horizontal and near the corresponding connector.
4. Check that multiplicities sit beside the correct association end.
5. Use **Format → Show Multiplicity** and **Format → Show Type** before final review.
6. Verify names against the Django source files `library/models.py`, `student/models.py`,
   `library/views.py`, and both URL configurations.
7. Save the `.mdj` file.
8. Export each diagram using **File → Export Diagram As → SVG** for scalable website display.
9. Use descriptive filenames such as `library_class_diagram.svg` and
   `library_deployment_diagram.svg`.
10. Open every exported SVG and inspect it at both fitted width and 200% zoom before submission.

### Official StarUML References

- [Managing Diagrams](https://docs.staruml.io/user-guide/managing-diagrams)
- [Class Diagram](https://docs.staruml.io/working-with-uml-diagrams/class-diagram)
- [Use Case Diagram](https://docs.staruml.io/working-with-uml-diagrams/use-case-diagram)
- [Sequence Diagram](https://docs.staruml.io/working-with-uml-diagrams/sequence-diagram)
- [Communication Diagram](https://docs.staruml.io/working-with-uml-diagrams/communication-diagram)
- [Statechart Diagram](https://docs.staruml.io/working-with-uml-diagrams/statechart-diagram)
- [Activity Diagram](https://docs.staruml.io/working-with-uml-diagrams/activity-diagram)
- [Component Diagram](https://docs.staruml.io/working-with-uml-diagrams/component-diagram)
- [Deployment Diagram](https://docs.staruml.io/working-with-uml-diagrams/deployment-diagram)
- [Formatting Diagram Elements](https://docs.staruml.io/user-guide/formatting-diagram)
