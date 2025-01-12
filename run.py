# run.py
import streamlit as st
from components.markdown_func import markdown

def initialize_session_state():
    if "llm_initialized" not in st.session_state:
        st.session_state.llm_initialized = False
        
# 페이지 네비게이션 설정
def main():
    initialize_session_state()  # 메인 함수 시작 시 초기화 실행
    
    st.set_page_config(page_title="카드 추천 시스템", page_icon="💳", layout="wide")

    # 상태 완전 초기화
    st.session_state.result_page = False
    st.session_state.page = None
    st.session_state.selected_card = None
    st.session_state.messages = []
    st.session_state.llm_initialized = False  # LLM 초기화 상태 리셋
    if 'uploaded_file' in st.session_state:
        del st.session_state.uploaded_file
    if 'session_id' in st.session_state:
        del st.session_state.session_id
    
    st.title("카드 추천 시스템")
    st.write("보다 스마트한 카드 사용을 위한 OO! '맞춤형 카트 추천' 기능과 '챗봇 카트 추천' 가능을 통해 카드에 대해서 알아가보아요!")
    
    col1, col2 = st.columns(2)
    markdown()
    with col1:
        if st.button("맞춤형 카드 추천"):
            st.switch_page("pages/card.py")
            
    with col2:
        if st.button("챗봇 카드 추천"):
            st.switch_page("pages/llm.py")

if __name__ == "__main__":
    main()