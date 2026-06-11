"""
Step 2: Exploratory Data Analysis (EDA)
Purpose: Visualize price patterns by fuel type, seller type, transmission, and correlations.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Assuming car_data is already loaded from Step 1
# car_data = pd.read_csv('car_data.csv')

# Create price analysis by categorical features
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

# Price by Fuel Type
sns.barplot(x='Fuel_Type', y='Selling_Price', data=car_data, ax=axes[0])
axes[0].set_title('Average Price by Fuel Type')
axes[0].set_xlabel('Fuel Type')
axes[0].set_ylabel('Selling Price (Lakhs)')

# Price by Seller Type
sns.barplot(x='Seller_Type', y='Selling_Price', data=car_data, ax=axes[1])
axes[1].set_title('Average Price by Seller Type')
axes[1].set_xlabel('Seller Type')

# Price by Transmission
sns.barplot(x='Transmission', y='Selling_Price', data=car_data, ax=axes[2])
axes[2].set_title('Average Price by Transmission')
axes[2].set_xlabel('Transmission')

plt.tight_layout()
plt.show()

# Create correlation heatmap
fig, ax = plt.subplots(figsize=(10, 8))
numeric_columns = car_data.select_dtypes(include=['float64', 'int64']).columns
sns.heatmap(car_data[numeric_columns].corr(), annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
plt.title('Correlation between Numeric Columns')
plt.tight_layout()
plt.show()

# Optional: Additional visualizations
print("EDA Summary:")
print(f"Total records: {len(car_data)}")
print(f"\nFuel Type Distribution:\n{car_data['Fuel_Type'].value_counts()}")
print(f"\nSeller Type Distribution:\n{car_data['Seller_Type'].value_counts()}")
print(f"\nPrice Range: {car_data['Selling_Price'].min():.2f} - {car_data['Selling_Price'].max():.2f} Lakhs")
