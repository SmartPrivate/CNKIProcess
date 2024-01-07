import streamlit as st
import pandas as pd

with st.sidebar:
    uploaded_file = st.file_uploader(label='请选择你需要进行分析的中国知网导出文件：')
    df = pd.read_csv(uploaded_file)
    print(df)