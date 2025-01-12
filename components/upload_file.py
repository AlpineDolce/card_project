# upload_file.py
import streamlit as st

def upload_file():
    # 결과 페이지일 때 사용자 정보 숨기기
    if st.session_state.get('result_page', False):
        return
    """가계부 파일 업로드 처리"""
    st.subheader("원하시는 카드 혜택을 선택하세요")
    st.write("가계부를 .xlsx, .pdf 형태로 업로드 하세요")
    
    # 파일 업로드 시 확장자 제한 (.xlsx, .pdf)
    uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "pdf"])
    
    if uploaded_file is not None:
        # 업로드된 파일의 확장자 체크
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension in ["xlsx", "pdf"]:
            st.session_state.uploaded_file = uploaded_file  # 업로드된 파일 저장
            st.write(f"File uploaded: {uploaded_file.name}")
        else:
            st.error("허용되지 않는 파일 형식입니다. .xlsx 또는 .pdf 파일만 업로드 가능합니다.")
            st.session_state.uploaded_file = None
    else:
        st.session_state.uploaded_file = None  # 파일이 없으면 None 저장