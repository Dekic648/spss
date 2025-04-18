import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="No-Code SPSS", layout="wide")

st.title("📊 No-Code SPSS (Grouped Charts Edition)")

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

    st.markdown("## 🔢 Average Ratings (Total)")
    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
    if numeric_columns:
        avg_stats = df[numeric_columns].mean().round(2).to_frame("Average").T
        st.dataframe(avg_stats)

    st.markdown("## 🧩 Segment-Based Analysis")
    segment_col = st.selectbox("Segment by", df.select_dtypes(exclude=np.number).columns)
    selected_question = st.selectbox("Choose a numeric question to split by segment", numeric_columns)

    if segment_col and selected_question:
        segment_means = df.groupby(segment_col)[selected_question].mean().sort_values(ascending=False)
        st.bar_chart(segment_means)

    st.markdown("## 📋 Multiple Choice Analysis")
    mc_columns = detect_multiple_choice_columns(df)
    if mc_columns:
        st.markdown("### Detected Multiple Choice Options")
        mc_question = st.multiselect("Select multiple choice options", mc_columns, default=mc_columns)
        if mc_question:
            counts = df[mc_question].notna().sum().sort_values(ascending=False)
            percentages = counts / len(df) * 100
            st.bar_chart(percentages)

            st.markdown("### Segment Comparison with Grouped Bar Chart")
            segment_mc = st.selectbox("Segment by for multiple choice", df.select_dtypes(exclude=np.number).columns, key="seg_mc")

            grouped_data = {}
            for option in mc_question:
                grouped_data[option] = df.groupby(segment_mc)[option].apply(lambda x: x.notna().mean() * 100)

            segment_labels = df[segment_mc].dropna().unique()
            fig = go.Figure()
            for option in mc_question:
                fig.add_trace(go.Bar(
                    name=option,
                    x=segment_labels,
                    y=[grouped_data[option].get(seg, 0) for seg in segment_labels]
                ))
            fig.update_layout(
                barmode='group',
                title="Grouped Bar Chart: Feature Usage by Segment",
                xaxis_title=segment_mc,
                yaxis_title="Percentage (%)"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Data tables section (at the bottom)
    st.markdown("## 📊 Raw Data Table")
    st.dataframe(df.head())

    st.markdown("## 📈 Full Summary Statistics")
    st.write(df.describe(include='all'))