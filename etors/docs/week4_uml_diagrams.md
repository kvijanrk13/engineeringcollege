# Week 4 and Week 5 - UML Design Models

The following UML models represent the E-Ticketing Online Reservation System (ETORS) design. Each diagram is reverse-checked against the Django models, URL routes, views, services, and templates implemented in the ETORS module. Multiplicities and message names reflect the actual implementation rather than a generic example.

## 1. Class Diagram

![ETORS class diagram](/static/etors/images/uml_diagrams/page1_uml_diagram.jpeg)

The class diagram models the ETORS domain with its principal associations between Station, Train, Booking, Passenger, CabBooking, CabCallLog, and User entities. Relationships follow Django ForeignKey and OneToOneField patterns.

## 2. Use Case Diagram

![ETORS use case diagram](/static/etors/images/uml_diagrams/page2_uml_diagram.png)

The primary actors are Passenger, Cab Driver, and Administrator/Librarian. The diagram covers train search, authentication, booking, payment, PNR management, BOOKMYCAB workflows, and system administration.

## 3. Sequence Diagram

![ETORS sequence diagram](/static/etors/images/uml_diagrams/page3_uml_diagram.jpeg)

This interaction traces the complete booking lifecycle: train search, passenger detail entry, fare calculation, availability recheck, booking creation, PNR generation, seat allocation, and confirmation display.

## 4. Collaboration Diagram

![ETORS collaboration diagram](/static/etors/images/uml_diagrams/page4_uml_diagram.jpeg)

The collaboration diagram presents the same runtime behavior as numbered messages between participating objects. It emphasizes object links and responsibility distribution rather than time on a vertical axis.

## 5. Statechart Diagram

![ETORS statechart diagram](/static/etors/images/uml_diagrams/page5_uml_diagram.jpeg)

The state machine models a Booking record through Confirmed, Cancelled, and related states. Guards correspond to payment confirmation, cancellation requests, and seat availability checks.

## 6. Activity Diagram

![ETORS activity diagram](/static/etors/images/uml_diagrams/page6_uml_diagram.jpeg)

Swimlanes separate Passenger, Django System, and Administrator responsibilities across search, booking, payment, PNR verification, cancellation, and BOOKMYCAB workflows.

## 7. Component Diagram

![ETORS component diagram](/static/etors/images/uml_diagrams/page7_uml_diagram.jpeg)

The component view shows the browser, Django routing and views, templates, domain models, ORM, business services, PostgreSQL, Google OAuth, and Render infrastructure with their provided dependencies.

## 8. Deployment Diagram

![ETORS deployment diagram](/static/etors/images/uml_diagrams/page8_uml_diagram.jpeg)

The deployment model reflects the production topology: user browser over HTTPS, Gunicorn and Django on the Render web service, Render PostgreSQL through `DATABASE_URL`, and Google OAuth for authentication.

## UML Notation

| Notation | Meaning |
|---|---|
| `1`, `0..1`, `0..*` | Relationship multiplicity |
| Arrowless solid line in class diagrams | Model association (ForeignKey or OneToOneField) |
| Dashed connector | Dependency, reply, or external integration |
| Open arrowhead in behavioral diagrams | Message or transition direction |
| Filled initial node / bullseye | Initial state / final state |

## Detailed StarUML Drawing Procedure

### A. Common Project Setup

1. Open StarUML and select **File → New**.
2. In **Model Explorer**, rename the root model to `ETORS`.
3. Right-click the root model and create packages with **Add → Package** as needed.
4. To add any diagram, first select the root model or the package that should own it. Then use **Model → Add Diagram → [Diagram Type]**.
5. Rename every diagram immediately in Model Explorer.
6. Keep the **Toolbox**, **Model Explorer**, and **Property Editor** visible. Double-clicking an element, or selecting it and pressing `Enter`, opens QuickEdit.
7. Use a white diagram background, black connectors, and one font family throughout.
8. Use **Format → Show Type**, **Format → Show Visibility**, **Format → Show Multiplicity**, and **Format → Show Operation Signature** where applicable.
9. Save the project before drawing. Save again after completing each diagram.
10. After drawing, inspect every connector at 100% and 150% zoom.

### B. Class Diagram

#### Step 1: Create the diagram and classes

1. Select the root model and choose **Model → Add Diagram → Class Diagram**.
2. Draw the ETORS classes: `Station`, `Train`, `Booking`, `Passenger`, `CabBooking`, `CabCallLog`, and `auth.User`.
3. Arrange classes to reflect their functional grouping.

#### Step 2: Enter attributes and operations

1. Select each class and press `Ctrl+Enter` to add attributes.
2. Enter attributes using `- name : Type` notation.
3. Add primary keys, foreign keys, and descriptive fields as per the Django models.
4. Press `Ctrl+Shift+Enter` to add operations such as `__str__() : String`.

#### Step 3: Draw correct model associations

1. Select **Association**, not Generalization, Aggregation, or Composition.
2. Draw associations matching ForeignKey and OneToOneField relationships.
3. Set multiplicities: `1` for the "one" side, `0..*` for the "many" side.
4. Keep associations arrowless. A hollow triangle means inheritance.
5. Use **Format → Show Multiplicity** if endpoint values are hidden.

#### Step 4: Final class-diagram validation

1. Confirm that every ForeignKey has a solid association.
2. Confirm multiplicities match the Django model definitions.
3. Confirm that only actual dependencies are dashed.
4. Move labels so that no class border, attribute, or multiplicity is covered.

### C. Use Case Diagram

1. Select the root model and add a **Use Case Diagram**.
2. Draw a **Use Case Subject** and name it `ETORS`.
3. Place `Passenger`, `Cab Driver`, and `Administrator` actors outside the subject.
4. Inside the subject, add use cases for all ETORS functions.
5. Connect actors to their respective use cases with **Association**.
6. Keep actors outside the system boundary and all use cases inside it.

### D. Sequence Diagram

1. Add a **Sequence Diagram** under the root model.
2. Add Lifelines for each participant in the booking workflow.
3. Keep equal horizontal spacing and extend all lifelines to the same lower boundary.
4. Add synchronous messages in workflow order.
5. Add dashed Reply Messages for responses.
6. Use solid arrows for calls and dashed arrows for replies.
7. Time must progress strictly downward.

### E. Collaboration/Communication Diagram

1. Add a **Communication Diagram**.
2. Add Lifelines or object roles for each participant.
3. Arrange the objects around an open center so connector labels remain visible.
4. Use **Connector** to link only objects that directly exchange messages.
5. Add messages with hierarchical numbering.
6. Confirm that the same scenario and ordering are represented in both Sequence and Communication diagrams.

### F. Statechart Diagram

1. Add a **Statechart Diagram**.
2. Place an **Initial State** at the far left.
3. Add states relevant to the ETORS entity being modeled.
4. Add an **Activity Final** state after the final state.
5. Draw **Transition** elements with event names, guards, and effects.
6. Put event names before `/`, guards inside `[ ]`, and effects after `/`.
7. Verify that every non-final state has a valid outgoing path.

### G. Activity Diagram

1. Add an **Activity Diagram**.
2. Draw vertical **Swimlanes** named `Passenger`, `Django System`, and `Administrator`.
3. Put an **Initial Node** at the top of the Passenger lane.
4. Add actions in each lane corresponding to the responsible party.
5. Connect the actions with **Control Flow** in execution order.
6. Place a **Decision Node** where branching occurs.
7. Add an **Activity Final Node** at the end.
8. Ensure every action is placed in the lane of the party responsible for performing it.

### H. Component Diagram

1. Add a **Component Diagram**.
2. Add components named `Browser`, `Django URL Router`, `Views`, `Templates`, `Domain Models`, `ORM`, and `Business Services`.
3. Add external/database components named `PostgreSQL`, `Google OAuth`, and `Render`.
4. Arrange Browser on the left, application components in the center, and external services on the right.
5. Use **Dependency** arrows for "uses" relationships.
6. Confirm that no database or external API is drawn as an internal Django module.

### I. Deployment Diagram

1. Add a **Deployment Diagram**.
2. Add a Node named `User Device` with stereotype `«device»`.
3. Place a `Web Browser` artifact inside it.
4. Add a large Node named `Render Web Service` with stereotype `«execution environment»`.
5. Inside the Render node, place `Gunicorn`, `Django Application`, `Templates / Static Files`, and `Django ORM`.
6. Add a Node named `Render PostgreSQL` with stereotype `«database node»`.
7. Place the database artifact inside the PostgreSQL node.
8. Select **Communication Path** and connect Device to Render Web Service. Label it `HTTPS`.
9. Connect Render Web Service to Render PostgreSQL and label it `TLS / DATABASE_URL`.
10. Add a Note containing build and runtime information.
11. Verify that physical/runtime nodes contain deployable artifacts.

### J. Formatting, Review, and Export

1. Select related elements and use **Format → Align** and **Format → Distribute** for consistent spacing.
2. Increase the default font until labels remain readable.
3. Keep relationship labels horizontal and near the corresponding connector.
4. Check that multiplicities sit beside the correct association end.
5. Verify names against the Django source files.
6. Save the `.mdj` file.
7. Export each diagram using **File → Export Diagram As → SVG** for scalable website display.
8. Open every exported diagram and inspect it before submission.

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
