## Cleaned & Feature Engineered Car Price Dataset
## Note: 
This dataset does not belong to me. I originally got the dataset on Kaggle from 'taeefnajib'. I needed a dataset for a prediction model so i cleaned this up, removed null values and added new columns.
Do not note that the not all the filled null values are accurately. this why you can see some electric cars having V6 engines. However, a lot of empty horsepower columns have been crossreferenced from wikipedia and brand websites
and then filled.

Also i did not encode columns. I did that so if someone chose to implement their own encoding methods, they would atleast know what the column values actually mean.

Lastly, the dataset is basivally ready to use which some minor preprocessing. Thanks again to 'taeefnajib' for prividing me with the dataset.

### Source
Original dataset: [Used Car Price Prediction Dataset](https://www.kaggle.com/datasets/taeefnajib/used-car-price-prediction-dataset)

### Modifications
- Extracted horsepower, layout and engine capacity from the existing dataset
- filled all the null values, most of them are crossreferenced from reputable sources.
- Data is left is verbose state so people can understand them when encoding

### Files
- `used_car_cleaned.csv`: Final processed dataset ready for ML use, preferrable Regression

### Columns

- **brand** — Manufacturer or company name of the car (e.g., Toyota, BMW).  
- **model_year** — Year in which the car model was manufactured or launched.  
- **milage** — Total distance the car has traveled, in miles.  
- **fuel_type** — Type of fuel used by the car (e.g., Petrol, Diesel, Electric).  
- **transmission** — Gear system type of the car, such as Manual or Automatic.  
- **accident** — Indicates whether the car has been in any reported accidents.  
- **clean_title** — Shows if the car has a clean, non-salvage ownership title.  
- **price** — The listed or market price of the car.  
- **horsepower** — Engine power output, measured in HP (horsepower).  
- **engine_capacity** — Volume of the engine, usually in liters (e.g., 2.0L).  
- **layout** — Engine layout (i4,v6,v8).  
- **model** — Specific model name of the car (e.g., Corolla, Civic, 3 Series).  
- **engine** — Verbose engine name.
