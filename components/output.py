import streamlit as st
import uuid
from ai_tools.llm_response import get_llm_response
from ai_tools.filter_module import get_combined_filter
import re
import plotly.graph_objects as go
import json
from ai_tools.llm_response import initialize_llm


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []  # 챗봇 메시지 초기화
    st.session_state.stream_buffer = ""
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  # 세션 ID 초기화
if "llm_initialized" not in st.session_state:
    st.session_state.llm_initialized = False  # LLM 초기화 상태 추가
if "generated_responses" not in st.session_state:
    st.session_state.generated_responses = []  # 이미 생성된 응답을 추적
if "selected_card" not in st.session_state:
    st.session_state.selected_card = None  # 선택된 카드 초기화
if "loading" not in st.session_state:
    st.session_state.loading = False  # 로딩 상태 추적


def show_loading_modal():
    st.markdown("""
        <style>
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 24px;
                z-index: 9999;
            }
            .loading-container {
                display: flex;
                align-items: center;  /* 수평 정렬 */
                justify-content: center;  /* 콘텐츠 중앙 배치 */
                font-size: 24px;  /* 글자 크기와 일치시킴 */
            }
            /* 부드러운 글자 깜빡임 애니메이션 */
            @keyframes soft-blink {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            .loading-text {
                animation: soft-blink 2s ease-in-out infinite; /* 부드러운 깜빡임 */
            }
        </style>
        <div class="modal">
            <div class="loading-container">
                <p class="loading-text">답변을 생성 중입니다. 잠시만 기다려주세요...</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
def extract_expenses(text):
    # 정규표현식을 사용하여 카테고리와 퍼센트를 추출
    pattern = r'([가-힣\s]+)\((\d+\.?\d*)%\)'
    matches = re.findall(pattern, text)
    # 카테고리와 퍼센트를 분리하여 저장
    categories = []
    percentages = []
    for match in matches:
        category = match[0].strip()
        percentage = float(match[1])
        categories.append(category)
        percentages.append(percentage)
    return categories, percentages
def create_pie_chart_plotly(categories, percentages):
    # 파이 차트 생성
    fig = go.Figure(
        data=[
            go.Pie(
                labels=categories,
                values=percentages,
                hoverinfo="label+percent",
                textinfo="value+percent",
                textfont=dict(size=14),
                marker=dict(colors=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC',
                                     '#99CCFF', '#FF99FF', '#99FFCC', '#FFB366', '#FF99AA'])
            )
        ]
    )
    # 레이아웃 설정
    fig.update_layout(
        title={
            'text': "월간 지출 분석",
            'y': 0.9,  # 타이틀의 Y 위치
            'x': 0.5,  # 타이틀의 X 위치
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend=dict(
            title="지출 항목",
            orientation="v",  # 수직 정렬
            yanchor="top",
            y=1.05,
            xanchor="left",
            x=0.9
        )
    )
    return fig
def output():
    # 세션 상태 초기화 (함수 시작 부분에 추가)
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "stream_buffer" not in st.session_state:
        st.session_state.stream_buffer = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # 타이틀과 홈 버튼을 한 줄에 배치
    col_title, _, col_home = st.columns([6, 1.3, 1])
    with col_title:
        st.title("사용자 특화 카드 추천 시스템")
    with col_home:
        if st.button('🏠 홈으로 가기', help='홈으로 가기'):
            # 세션 상태 초기화
            st.session_state.messages = []  # 챗봇 메시지 초기화
            st.session_state.result_page = False
            st.session_state.generated_responses = []  # 이전 응답 초기화
            st.session_state.stream_buffer = ""  # 스트림 버퍼 초기화
            st.session_state.selected_card = None  # 선택된 카드 초기화
            st.session_state.session_id = str(uuid.uuid4())  # 새로운 세션 ID 생성
            # LLM 응답을 새로 생성할 수 있도록 설정
            st.session_state.llm_initialized = False
            st.session_state.last_page = "llm"  # 이전 페이지 정보 추가 (필요 시 활용)
            st.switch_page("run.py")  # 홈 화면으로 돌아가기
            
    
    
    if not st.session_state.llm_initialized and st.session_state.result_page:
        # 로딩 모달을 화면에 표시
        st.session_state.loading = True
        show_loading_modal()
        
        
        # 동적으로 가져오기
        def load_json_file(file_path):
            # JSON 파일 읽기
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)

        # 파일 경로 직접 제공
        module_name = "data/user_info_output.json"  # 이미 경로 지정됨
        user_info_output = load_json_file(module_name)


        ##
        decision_prompt = f""" 다음은 나에 대한 정보야. 이걸 토대로 신용카드 추천을 해줘
        [정보]
        {user_info_output}
        """
        combined_filter = get_combined_filter(user_info_output)
        # LLM 응답 생성
        for chunk in get_llm_response(decision_prompt, st.session_state.session_id, combined_filter):
            st.session_state.stream_buffer += chunk
        st.session_state.messages.append(
            {"role": "user", "content": decision_prompt}
        )
        # 응답을 세션에 저장
        st.session_state.messages.append(
            {"role": "assistant", "content": st.session_state.stream_buffer}
        )
        st.session_state.generated_responses.append(decision_prompt)  # 생성된 응답을 추적
        st.session_state.stream_buffer = ""  # 스트림 버퍼 초기화
        # LLM 응답이 완료되었으면 로딩을 숨기고 답장을 보여줌
        st.session_state.loading = False
        st.session_state.llm_initialized = True
        st.rerun()  # UI 새로고침

    if st.session_state.llm_initialized and st.session_state.result_page:
        # 이전 메시지들을 출력
        for message in st.session_state.messages[1:]:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                # assistant의 응답에서 지출 내역이 있는 경우 파이 차트 생성
                if message["role"] == "assistant":
                    # 지출 내역이 포함된 문장 찾기
                    if "지출 내역" in message["content"]:
                        categories, percentages = extract_expenses(message["content"])
                        if categories and percentages:  # 데이터가 추출된 경우에만
                            fig = create_pie_chart_plotly(categories, percentages)
                            # 고유한 키를 추가하여 plotly_chart 호출
                            st.plotly_chart(fig, key=f"pie_chart_{st.session_state.session_id}")  # 고유한 키 추가
                            
        # 사용자 입력 처리
        if user_input := st.chat_input("채팅을 입력해주세요."):
            # LLM 초기화
            if not st.session_state.get("llm_initialized", False):
                initialize_llm()
                st.session_state.llm_initialized = True

            # 메시지 추가: 사용자 입력
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            # 비동기 스트림으로 LLM 응답 생성
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                session_id = st.session_state.session_id
                
                # 부드럽게 깜빡이는 로딩 메시지 표시
                response_placeholder.markdown("""
                    <style>
                        .loading-container {
                            display: flex;
                            align-items: center;  /* 수직 정렬 */
                            justify-content: flex-start;  /* 왼쪽 정렬 */
                            font-size: 16px;  /* 기본 글자 크기 */
                        }
                        @keyframes soft-blink {
                            0% { opacity: 1; }
                            50% { opacity: 0.5; }
                            100% { opacity: 1; }
                        }
                        .loading-text {
                            animation: soft-blink 2s ease-in-out infinite; /* 부드러운 깜빡임 */
                        }
                    </style>
                    <div class="loading-container">
                        <p class="loading-text">답변을 생성 중입니다. 잠시만 기다려주세요...</p>
                    </div>
                """, unsafe_allow_html=True)

                # 답변 생성 시작
                decision_prompt = user_input  # 사용자 입력을 그대로 사용
                for chunk in get_llm_response(decision_prompt, session_id):
                    st.session_state.stream_buffer += chunk
                    response_placeholder.write(st.session_state.stream_buffer)

            # 전체 응답 저장
            st.session_state.messages.append(
                {"role": "assistant", "content": st.session_state.stream_buffer}
            )
            st.session_state.stream_buffer = ""  # 스트림 버퍼 초기화