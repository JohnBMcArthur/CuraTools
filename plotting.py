import streamlit as st
import pandas as pd
import io
import numpy as np
import os
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import csv

def parse_excel_paste(excel_clipboard):
    # Use StringIO to simulate a file object from the pasted string.
    data = io.StringIO(excel_clipboard)
    try:
        # Assume tab-delimited data, which is common when copying from Excel
        return pd.read_csv(data, sep='\t')
    except Exception as e:
        # Display an error in the app if the data could not be parsed
        st.error(f"Failed to parse data: {e}")
        return None

#Curve fitting for DC T50 values
# Data scaling function
# Change min and max values if assay range changes
def data_scaling(column, min_val, max_val):
    max_val = column.max()
    scaled_data = (column - min_val) / (max_val - min_val)
    return scaled_data, min_val, max_val

# Inverse data scaling function
def inverse_data_scaling(scaled_data, min_val, max_val):
    return scaled_data * (max_val - min_val) + min_val

# Curve fitting function
def fit_curve(x, lc50, hill_coefficient):
    return 1 / (1 + (lc50/x) ** hill_coefficient)

# Process a single column and sample from a DataFrame
def process_column(df, col_letter, min_val, max_val):
    x_data = df['Temp'].values
    y_data = df[col_letter].values
    scaled_data_col, _, _ = data_scaling(y_data, min_val, max_val)
    
    try:
        popt, covar = curve_fit(fit_curve, x_data, scaled_data_col, bounds=([0, -np.inf], [100, 0]))
        lc50_fit, hill_coefficient_fit = popt
    except RuntimeError as e:
        st.error(f"An error occurred for Sample: {col_letter} - {e}")
        lc50_fit = hill_coefficient_fit = np.nan  # Set NaN values for failed fits
    
    return lc50_fit, hill_coefficient_fit, x_data, y_data

# Main function adapted for Streamlit
def calc_hill(df, min_val, y_axis, x_axis):
    output_list = []
    for col_letter in df.columns[1:]:  # Assuming first column is 'Temp'
        lc50_fit, hill_coefficient_fit, x_data, y_data = process_column(df, col_letter, min_val, 140000)  # max_val is hardcoded for now
        st.write(f"Sample: {col_letter}")
        st.write(f"Dilution Factor at curve midpoint: {lc50_fit}, Hill Coefficient Fit: {hill_coefficient_fit}")
        output_list.append((col_letter, lc50_fit, hill_coefficient_fit))



