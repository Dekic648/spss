import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

st.set_page_config(page_title="No-Code SPSS", layout="wide")

st.title("📊 No-Code SPSS (Demo)")
st.markdown("Upload your dataset and explore descriptive stats, T-tests, and multiple choice summaries.")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

def detect_multiple_choice_columns(df, threshold=0.8):
    mc_cols = []
    for col in df.columns:
        filled_ratio = df[col].notna().mean()
        unique_vals = df[col].dropna().unique()
        if 0 < filled_ratio < threshold and len(unique_vals) < 10:
            mc_cols.append(col)
    return mc_cols

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    st.subheader("Data Preview")
    st.dataframe(df.head())

    st.subheader("Basic Summary")
    st.write(df.describe(include='all'))

    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
    
    if numeric_columns:
        st.subheader("Histogram of Numeric Columns")
        col_to_plot = st.selectbox("Select column", numeric_columns)
        fig, ax = plt.subplots()
        df[col_to_plot].hist(bins=20, ax=ax)
        ax.set_title(f"Histogram of {col_to_plot}")
        st.pyplot(fig)

        st.subheader("T-Test Between Two Groups")
        group_column = st.selectbox("Group by (categorical)", df.select_dtypes(exclude=np.number).columns, key='group_col')
        value_column = st.selectbox("Value column (numeric)", numeric_columns, key='value_col')
        
        if group_column and value_column:
            groups = df[group_column].dropna().unique()
            if len(groups) == 2:
                group1 = df[df[group_column] == groups[0]][value_column].dropna()
                group2 = df[df[group_column] == groups[1]][value_column].dropna()
                t_stat, p_val = stats.ttest_ind(group1, group2)
                st.write(f"**T-test result:** p-value = {p_val:.4f}")
                if p_val < 0.05:
                    st.success("Significant difference between groups.")
                else:
                    st.info("No significant difference found.")
            else:
                st.warning("Please select a grouping column with exactly 2 unique values.")

    # MULTIPLE CHOICE ANALYSIS
    st.subheader("Multiple Choice Analysis")
    mc_columns = detect_multiple_choice_columns(df)

    if mc_columns:
        st.markdown("### Detected Multiple Choice Question:")
        mc_question = st.multiselect("Select options from the same multiple choice question", mc_columns, default=mc_columns)
        if mc_question:
            counts = df[mc_question].notna().sum().sort_values(ascending=False)
            percentages = counts / len(df) * 100
            st.bar_chart(percentages)

            st.markdown("### Segment Comparison")
            segment_col = st.selectbox("Segment by (categorical)", df.select_dtypes(exclude=np.number).columns, key="seg_compare")
            if segment_col:
                for option in mc_question:
                    st.markdown(f"#### 📌 {option}")
                    comparison = df.groupby(segment_col)[option].apply(lambda x: x.notna().mean() * 100)
                    st.bar_chart(comparison)
    else:
        st.info("No multiple choice columns detected (optional columns with non-empty values).")