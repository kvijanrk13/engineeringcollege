# Experiment design and interpretation

## Research themes represented

This executable demonstrator is an original implementation inspired by the cited review's discussion of interpretable feature pipelines, horizontal federation, privacy mechanisms, and evaluation gaps. It is not a reimplementation of a particular paper method and does not reproduce the review's prose, figures, or tables.

The generated task has six bounded inputs and a binary target with linear, interaction, and nonlinear signal. A fixed feature library adds named square and pairwise-product terms. Simulated clients hold disjoint horizontal partitions. A coordinator receives weighted gradients for a full-batch logistic objective; client records are not combined or sent by the simulation.

## Privacy boundary

Feature selection releases noisy mean feature-label scores. Each per-record contribution is clipped into `[-1, 1]`, giving replace-one sensitivity `2 / n_train` for the mean query. The Laplace mechanism uses scale `2 / (n_train * epsilon)` and reports `delta = 0`.

This guarantee does **not** cover the model or training process. Federated gradients are unnoised, and this single-process simulation does not provide secure aggregation, transport security, or client isolation. Treat the experiment as a teaching prototype, not a privacy-certified system.

## Evaluation

The program uses a seeded synthetic dataset, a stratified holdout split, named selected features, and a deterministic client partition. It reports accuracy, precision, recall, F1, and the absolute difference in recall between two synthetic protected groups. The group statistic is a diagnostic only; it is not a fairness guarantee or a substitute for domain-specific review.

No claim of real-world utility, clinical suitability, privacy certification, or production scalability is made. Evaluate alternative seeds, sample counts, feature budgets, client counts, and epsilon values before drawing conclusions.
