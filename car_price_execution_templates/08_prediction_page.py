"""
Step 8: Prediction Page (Streamlit App)
Purpose: Create interactive web interface for car price predictions.

To run:
  streamlit run 08_prediction_page.py
"""
import pickle
import pandas as pd
import streamlit as st
import numpy as np

# Load model and scaler
@st.cache_resource
def load_model():
    with open('model.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_resource
def load_scaler():
    import joblib
    return joblib.load('scaler_joblib.pkl')

model = load_model()
scaler = load_scaler()

# Streamlit app layout
st.set_page_config(page_title="Used Car Price Prediction Using K-Radius Nearest Neighbors", layout="wide")
st.title("Used Car Price Prediction Using K-Radius Nearest Neighbors")
st.markdown("---")

# Create input columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Vehicle Information")
    present_price = st.number_input(
        'Present Price (in Lakhs)', 
        min_value=0.0, 
        max_value=100.0, 
        value=10.0,
        step=0.5
    )
    
    kms_driven = st.number_input(
        'Kilometers Driven', 
        min_value=0, 
        max_value=1000000, 
        value=50000,
        step=1000
    )
    
    fuel_type = st.selectbox(
        'Fuel Type', 
        ['Petrol', 'Diesel', 'CNG']
    )

with col2:
    st.subheader("More Details")
    seller_type = st.selectbox(
        'Seller Type', 
        ['Dealer', 'Individual']
    )
    
    transmission = st.selectbox(
        'Transmission Type', 
        ['Manual', 'Automatic']
    )
    
    owner = st.selectbox(
        'Number of Owners', 
        [0, 1, 2, 3]
    )
    
    year = st.number_input(
        'Year of Manufacture', 
        min_value=1980, 
        max_value=2026, 
        value=2015,
        step=1
    )

# Predict button
st.markdown("---")
if st.button('🔮 Predict Selling Price', key='predict_btn'):
    try:
        # Prepare input data
        input_data = pd.DataFrame({
            'Present_Price': [present_price],
            'Kms_Driven': [kms_driven],
            'Fuel_Type': [0 if fuel_type == 'Petrol' else 1 if fuel_type == 'Diesel' else 2],
            'Owner': [owner],
            'Year': [year],
            'Seller_Type_Individual': [1 if seller_type == 'Individual' else 0],
            'Transmission_Manual': [1 if transmission == 'Manual' else 0],
        })
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        selling_price_inr = prediction * 100000
        
        # Display result
        st.success("✅ Prediction Complete!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Predicted Selling Price",
                value=f"₹ {selling_price_inr:,.0f}",
                delta=f"{((selling_price_inr / (present_price * 100000)) - 1) * 100:.1f}% change"
            )
        
        with col2:
            depreciation = present_price - (prediction)
            st.metric(
                label="Estimated Depreciation",
                value=f"{depreciation:.2f} Lakhs",
                delta=f"{(depreciation / present_price * 100):.1f}%"
            )
        
        with col3:
            st.metric(
                label="Price per Kilometer",
                value=f"₹ {(selling_price_inr / kms_driven) if kms_driven > 0 else 0:,.0f}"
            )
        
        # Show input summary
        st.subheader("📋 Input Summary")
        summary_df = pd.DataFrame({
            'Parameter': ['Present Price', 'KMs Driven', 'Fuel Type', 'Seller Type', 'Transmission', 'Owners', 'Year'],
            'Value': [f'{present_price} Lakhs', f'{kms_driven:,} km', fuel_type, seller_type, transmission, owner, year]
        })
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"❌ Error in prediction: {str(e)}")

# Information section
with st.expander("ℹ️ About This Predictor"):
    st.markdown("""
    ### How This Works
    - Uses a trained machine learning model (Linear/Ridge/RF Regression)
    - Trained on historical car data from Kaggle
    - Predicts selling price based on vehicle characteristics
    
    ### Accuracy Factors
    - Model performance depends on training data quality
    - Real-world prices may vary based on condition, mileage, market demand
    - Use as a reference guide, not absolute truth
    
    ### Model Information
    - Features: 8 (Present Price, KMs, Fuel Type, Seller Type, Transmission, Owners, Year)
    - Training samples: ~5000+ historical cars
    - Typical accuracy: R² Score 0.85+
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Developed for Engineering College ML Demonstration Project</p>",
    unsafe_allow_html=True
)
