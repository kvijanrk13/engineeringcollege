# Engineering College - UML Diagrams Documentation

## Overview
This directory contains PlantUML UML diagrams for the Engineering College project, organized by module:
- **ADMIN Module**
- **STUDENT Module**
- **FACULTY Module**

## Diagram List (Ordered by Type)

### 1. Class Diagrams
| File | Description |
|------|-------------|
| 01_Class_Diagram_Admin.puml | Class diagram showing Admin-specific entities and relationships |
| 02_Class_Diagram_Student.puml | Class diagram showing Student module classes |
| 03_Class_Diagram_Faculty.puml | Class diagram showing Faculty module classes |
| 24_Class_Diagram_Complete.puml | Complete class diagram with all modules combined |

### 2. ER Diagrams
| File | Description |
|------|-------------|
| 04_ER_Diagram_Admin.puml | Entity Relationship diagram for Admin module |
| 05_ER_Diagram_Student.puml | Entity Relationship diagram for Student module |
| 06_ER_Diagram_Faculty.puml | Entity Relationship diagram for Faculty module |
| 23_ER_Diagram_Complete.puml | Complete ER diagram for all modules |

### 3. Collaboration Diagrams
| File | Description |
|------|-------------|
| 10_Collaboration_Diagram_Admin.puml | Admin module collaboration diagram |
| 11_Collaboration_Diagram_Student.puml | Student module collaboration diagram |
| 12_Collaboration_Diagram_Faculty.puml | Faculty module collaboration diagram |

### 4. Deployment Diagram
| File | Description |
|------|-------------|
| 13_Deployment_Diagram.puml | System deployment architecture |

### 5. Sequence Diagrams
| File | Description |
|------|-------------|
| 14_Sequence_Diagram_Admin_Login.puml | Admin login sequence flow |
| 15_Sequence_Diagram_Student_Login.puml | Student login sequence flow |
| 16_Sequence_Diagram_Faculty_Login.puml | Faculty login sequence flow |

### 6. State Chart Diagrams
| File | Description |
|------|-------------|
| 17_State_Chart_Admin.puml | Admin module state transitions |
| 18_State_Chart_Student.puml | Student module state transitions |
| 19_State_Chart_Faculty.puml | Faculty module state transitions |

### 7. Use Case Diagrams
| File | Description |
|------|-------------|
| 20_Use_Case_Diagram_Admin.puml | Admin use cases |
| 21_Use_Case_Diagram_Student.puml | Student use cases |
| 22_Use_Case_Diagram_Faculty.puml | Faculty use cases |

## Module Permissions Summary

### Faculty Module Access
- Can use EXAMBRANCH
- Can use SYLLABUS
- Can use GALLERY
- Can do FACULTY FORM REGISTRATION

### Student Module Access
- Can use SYLLABUS
- Can use GALLERY
- Can do STUDENT FORM REGISTRATION

### Admin Module Access
- Maintains all data
- Populates dashboard
- Manages Faculty, Students, Subjects

## Excluded Components
The following components are NOT included in these diagrams:
- Car Price Prediction
- Cloudinary (except noted references)
- PhonePe Payment Gateway

## How to Generate Diagrams
```bash
# Using PlantUML CLI
java -jar plantuml.jar *.puml

# Or with VS Code PlantUML Extension
# Open .puml files and preview will auto-generate
```