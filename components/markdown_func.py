# markdown_func.py
import streamlit as st

def markdown():
    """스타일을 적용하는 함수"""
    st.markdown("""
        <style>
        .small-header {
            font-size: 20px;
            font-weight: bold;
        }
        .stButton > button {
            width: 100%;
            white-space: nowrap;
            padding: 10px 5px;
            margin: 0 5px;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)