from __future__ import annotations

from django.shortcuts import render

from apriori_analysis import apriori_rules, make_transactions
from dataset_loader import available_datasets, normalize_dataset

from .models import ExecutionLog


PROJECT_TITLE = "Predicting Second Hand Cars Price using Machine Learning Algorithms"


def index(request):
    dataset_key = request.GET.get("dataset", "cardekho-depreciation")
    if dataset_key not in available_datasets():
        dataset_key = "cardekho-depreciation"

    data = normalize_dataset(dataset_key)
    transactions = make_transactions(data)
    rules = apriori_rules(transactions, min_support=0.08, min_confidence=0.45)[:15]
    ExecutionLog.objects.create(
        algorithm="Apriori Association Rule Mining",
        dataset=dataset_key,
        rows_executed=len(data),
    )

    return render(
        request,
        "car_price_app/index.html",
        {
            "title": PROJECT_TITLE,
            "dataset_key": dataset_key,
            "datasets": available_datasets(),
            "row_count": len(data),
            "transaction_count": len(transactions),
            "rules": rules,
            "latest_runs": ExecutionLog.objects.order_by("-created_at")[:5],
        },
    )
