# Automated Test Notes

Automated tests are included in `Source Code/car_price_app/tests.py`.

Run from `Source Code/`:

```powershell
python manage.py test car_price_app
```

Covered checks:

- Dataset registry exposes the expected dataset keys.
- Dataset normalization returns required analytical columns.
- Training pipeline builds successfully.
- Prediction helper returns a numeric price when a model artifact exists.
- Registration and Apriori web pages return successful responses.

