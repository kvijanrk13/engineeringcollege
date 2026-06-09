# UML Diagrams

These Mermaid diagrams can be pasted into any Mermaid-enabled editor.

## Use Case Diagram

```mermaid
flowchart LR
    Student((Student))
    Admin((Faculty/Admin))
    Student --> Register[Register / Open App]
    Student --> Train[Train Model]
    Student --> Predict[Predict Car Price]
    Student --> Apriori[View Apriori Rules]
    Admin --> Review[Review Project Output]
```

## Component Diagram

```mermaid
flowchart TB
    UI[Django Templates]
    Views[Django Views]
    Loader[Dataset Loader]
    Trainer[Training Script]
    Predictor[Prediction Script]
    Apriori[Apriori Analysis]
    Data[(Datasets)]
    Artifacts[(Model Artifacts)]

    UI --> Views
    Views --> Loader
    Loader --> Data
    Trainer --> Loader
    Trainer --> Artifacts
    Predictor --> Artifacts
    Apriori --> Loader
```

## Activity Diagram

```mermaid
flowchart TD
    A[Start] --> B[Load Dataset]
    B --> C[Clean and Encode Fields]
    C --> D[Train/Test Split]
    D --> E[Train Regression Models]
    E --> F[Evaluate Metrics]
    F --> G[Save Best Model]
    G --> H[Run Prediction or Apriori Page]
    H --> I[End]
```
