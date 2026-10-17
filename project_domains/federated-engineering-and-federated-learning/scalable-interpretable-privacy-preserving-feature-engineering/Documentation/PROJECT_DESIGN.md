# Experiment design and interpretation

## Research themes represented

This executable demonstrator is an original implementation inspired by the cited review's discussion of interpretable feature pipelines, horizontal federation, privacy mechanisms, fairness, and evaluation gaps. It is not a reimplementation of a particular paper method and does not reproduce the review's prose, figures, or tables.

The review surveys work across centralized, horizontal, vertical, and hybrid federation. These arrangements differ in where records and attributes reside, so a feature-selection method or privacy claim in one arrangement does not automatically apply to another. This demo deliberately implements only horizontal federation: clients are disjoint row partitions and share weighted gradients with one coordinator in a single process.

The GUI offers three reproducible paths:

1. **Generated experiment:** create a binary classification task with six bounded features and known linear, interaction, and nonlinear signal.
2. **Labeled CSV:** process six numeric input columns (`x0` through `x5`), a binary `label`, and optional binary `protected_group`. The app engineers raw, square, and pairwise-interaction features; splits train and holdout rows; performs noisy feature ranking; trains the federated logistic model; and reports holdout measures.
3. **Single-record prediction:** enter six values and classify them with a model trained on a fresh, generated synthetic dataset. The entered record is not used to train that model.

The fixed feature library makes transformations explicit and selected coefficients inspectable. Candidate scores use a bounded feature-label statistic and Laplace noise; this illustrates one feature-selection privacy mechanism rather than a universal solution for federated feature engineering.

## Interpreting results and open evaluation questions

Accuracy, precision, recall, and F1 summarize different aspects of the holdout result; none alone demonstrates generalization to a real population. If the optional group column is supplied, the report compares recall across its two values. That gap is a diagnostic and does not establish fairness.

Privacy accounting must follow the whole data flow. The stated differential-privacy mechanism applies only to releasing the noisy feature-ranking scores. Model gradients, fitted coefficients, predictions, and evaluation metrics are not covered by that guarantee. No secure aggregation, network isolation, vertical federation, communication-cost measurement, or production threat protection is provided. The code and selected limitations therefore make these boundaries visible alongside the result.

The survey's cross-study comparison highlights why reproducible datasets, end-to-end privacy accounting, and consistent evaluation matter. This small experiment supplies an inspectable educational example, not a standardized benchmark or a replication of a reviewed method.

## Privacy boundary

Feature selection releases a vector of 13 noisy mean feature-label scores. Each per-record score coordinate is clipped into `[-1, 1]`, so the complete vector has replace-one L1 sensitivity `2 * 13 / n_train`. The Laplace mechanism uses scale `2 * 13 / (n_train * epsilon)` and reports `delta = 0`.

This guarantee does **not** cover the model or training process. Federated gradients are unnoised, and this single-process simulation does not provide secure aggregation, transport security, or client isolation. CSV uploads are limited to 1 MB and 5,000 rows, processed in memory for the request, and are not intentionally persisted by this app. Do not upload identifiable or sensitive records unless you are authorized and accept the service's hosting and processing terms. Treat the experiment as a teaching prototype, not a privacy-certified system.

## Evaluation

The program uses a seeded synthetic dataset, a stratified holdout split, named selected features, and a deterministic client partition. It reports accuracy, precision, recall, F1, and the absolute difference in recall between two synthetic protected groups. The group statistic is a diagnostic only; it is not a fairness guarantee or a substitute for domain-specific review.

No claim of real-world utility, clinical suitability, privacy certification, or production scalability is made. Evaluate alternative seeds, sample counts, feature budgets, client counts, and epsilon values before drawing conclusions.
