# UML-Derived Test Cases

These test cases are derived from the updated UML diagrams for Admin, Customer, Telangana RTA context, model training, prediction, Apriori mining, database logging, and deployment.

## Use Case Diagram Test Cases

| Test Case ID | Actor | Scenario | Steps | Expected Result |
|---|---|---|---|---|
| UML-UC-01 | Admin | Manage dataset | Open execution workflow, select dataset, load records | Dataset loads without missing-file error |
| UML-UC-02 | Admin | Train price model | Run `train_model.py --dataset cardekho-depreciation` | Model artifact and metrics are generated |
| UML-UC-03 | Admin | Review model metrics | Open/read `artifacts/metrics.json` | MAE, RMSE, R2, and row counts are available |
| UML-UC-04 | Admin | Run Apriori mining | Open `/apriori/` or run `apriori_analysis.py` | Frequent rules are displayed |
| UML-UC-05 | Customer | Enter vehicle details | Submit year, mileage, fuel, transmission, make, model, engine size | Input is accepted for prediction |
| UML-UC-06 | Customer | Predict used-car price | Run prediction command or submit prediction page | Predicted price is displayed |
| UML-UC-07 | Customer | View depreciation advice | Provide original price with vehicle details | Depreciation amount/percentage or advice is shown |
| UML-UC-08 | Telangana RTA | Provide registration context | Supply registration year and ownership count | Vehicle age and ownership factors are used |

## Class Diagram Test Cases

| Test Case ID | Class/Module | Scenario | Expected Result |
|---|---|---|---|
| UML-CL-01 | DatasetLoader | `available_datasets()` is called | Dataset keys include `cardekho-depreciation` |
| UML-CL-02 | DatasetLoader | `normalize_dataset()` is called | Output contains vehicle age, mileage, fuel, transmission, and target price |
| UML-CL-03 | TrainingPipeline | `build_pipeline()` is called | Pipeline includes `preprocessor` and `model` steps |
| UML-CL-04 | Predictor | `predict()` is called with a saved artifact | Numeric predicted price is returned |
| UML-CL-05 | AprioriAnalyzer | Transactions are generated from normalized records | Rules contain antecedent, consequent, support, and confidence |
| UML-CL-06 | ExecutionLog | Apriori page is opened | Execution log row is created |
| UML-CL-07 | StudentRegistration | Registration form is submitted | Registration data is saved in SQLite |

## Activity Diagram Test Cases

| Test Case ID | Flow | Steps | Expected Result |
|---|---|---|---|
| UML-ACT-01 | Admin training flow | Load dataset, clean fields, train pipeline, save metrics | Training completes and artifacts exist |
| UML-ACT-02 | Customer prediction flow | Enter car details, load model, predict price | Customer receives a predicted resale price |
| UML-ACT-03 | Telangana RTA context flow | Provide registration year and ownership count | Vehicle age and ownership count influence prediction features |
| UML-ACT-04 | Apriori branch | Request mining from Admin flow | Association rules are generated and shown |

## Sequence Diagram Test Cases

| Test Case ID | Interaction | Expected Result |
|---|---|---|
| UML-SEQ-01 | Admin -> Django View -> Dataset Loader | View receives normalized dataframe |
| UML-SEQ-02 | Django View -> Training Pipeline -> Artifacts | `car_price_model.joblib` and `metrics.json` are saved |
| UML-SEQ-03 | Customer -> Django View -> Telangana RTA Context | Registration age and ownership context are available for prediction |
| UML-SEQ-04 | Django View -> Predictor -> Artifacts | Predictor loads the trained model and returns price |

## Component and Deployment Test Cases

| Test Case ID | Component | Scenario | Expected Result |
|---|---|---|---|
| UML-CMP-01 | Django URLs and Views | Open `/`, `/apriori/`, `/maruti-prices/` after sign-in flow | Correct pages render |
| UML-CMP-02 | Dataset folder | Missing dataset file is detected | Clear file-not-found error is raised |
| UML-CMP-03 | Local artifacts | Prediction runs before training | User receives missing-artifact error |
| UML-DEP-01 | Local virtual environment | Install requirements and run Django checks | System check passes |
| UML-DEP-02 | SQLite database | Run migrations | Required tables are created |

## ER Diagram and Reverse-Engineering Test Cases

| Test Case ID | Diagram Source | Scenario | Expected Result |
|---|---|---|---|
| UML-ER-01 | `graph_models` ER diagram | Generate automatic ER PNG | `08_Automatic_ERD_graph_models.png` exists |
| UML-ER-02 | Hand-authored ER diagram | Compare entities with models | Student registration and execution log entities match model fields |
| UML-REV-01 | `pyreverse` class diagram | Generate reverse-engineered class PNG | `09_Automatic_Class_Diagram_pyreverse.png` exists |
| UML-REV-02 | `pyreverse` package diagram | Generate package PNG | `10_Automatic_Package_Diagram_pyreverse.png` exists |

