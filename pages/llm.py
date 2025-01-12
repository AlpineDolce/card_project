import streamlit as st
from components.markdown_func import markdown
import uuid
import re
from ai_tools.llm_response import get_llm_response

# "홈으로 가기" 버튼을 추가하여 홈 페이지로 돌아가도록
col_title, _, col_home = st.columns([6, 1.3, 1])
markdown()
with col_title:
    st.title("카드 추천 챗봇")
with col_home:
    if st.button('🏠 홈으로 가기', help='홈으로 가기'):
        st.session_state.session_id = str(uuid.uuid4())  # 새로운 세션 ID 초기화
        st.switch_page("run.py")

st.markdown("안녕하세요! 챗봇을 통해 원하시거나 궁금하신 카드가 있으시면 언제든 말씀해주세요!<br><br>카드 추천 받을 시 하기의 예시를 참고하여 질문하시면 상세히 답변드립니다!", unsafe_allow_html=True)
st.success("**예시**: 월 O만원 정도의 OO비 지출이 있는데 OO비 혜택이 있으면서도 연회비가 O만원인 'OO카드(카드社)' 추천해줘.")

# 세션 상태 초기화
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  # 새로운 세션 ID 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []  # 메시지 초기화
if "stream_buffer" not in st.session_state:
    st.session_state.stream_buffer = ""  # 스트림 버퍼 초기화

# 기존 메시지 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력 처리
if user_input := st.chat_input("채팅을 입력해주세요."):
    # # 사용자가 실제로 채팅을 시작할 때 LLM 초기화
    # if not st.session_state.get("llm_initialized", False):
    #     initialize_llm()
    #     st.session_state.llm_initialized = True

    # 메시지 추가: 사용자 입력
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 비동기 스트림으로 LLM 응답 생성
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        session_id = st.session_state.session_id
        
        # 로딩 메시지 표시
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
        # 카드 추천 요청 처리
        if re.search(r"(카드 추천|카드 추천 해줘|추천해줘)", user_input):
            # 사용자가 카드 추천을 요청한 경우
            decision_prompt = f"""사용자가 요청한 카드 추천 정보: {user_input}\n
            이전에 제공된 지출 내역이나 파일 데이터는 절대로 사용하지 마세요. 오직 사용자가 제공한 새로운 질문이나 요청에 대해서만 답변해주세요. 
            '카드 추천', '카드 추천 해줘', '추천해줘'와 같은 요청에도, 이전 데이터는 절대로 참조하지 않고 새로운 정보만을 바탕으로 카드 추천을 진행하세요.
            그리고 아무런 서술 없이 '카드 추천', '카드 추천 해줘', '추천해줘'라고 하면 무엇을 원하는지 더 자세히 물어보는 쪽으로 해주세요.
            사용자가 특정 카드사를 요구 시 해당 카드사의 카드를 추천해주고 카드사에서 나온 카드가 맞는지 다시 확인하세요."""

        else:
            # 카드 추천 외의 요청 처리
            decision_prompt = f"""사용자가 입력한 질문: {user_input}\n
            이전에 제공된 지출 내역이나 파일 데이터는 절대로 사용하지 마세요. **user_input을 통해 새로 받은 질문에 대해서만 자연스러운 응답**을 생성해 주세요.
            그리고 사용자 입장에서 자연스럽게 카드 이야기로 이어갈 수 있도록 유도해주세요.
            사용자가 카드사 물어보는 것 외에는 특정 카드사를 편향해서 언급하지 마세요."""

        # LLM 응답 스트리밍 처리
        for chunk in get_llm_response(decision_prompt, session_id):
            st.session_state.stream_buffer += chunk
            # 그 외의 응답은 계속해서 표시
            response_placeholder.write(st.session_state.stream_buffer)

    # 전체 응답 저장
    st.session_state.messages.append(
        {"role": "assistant", "content": st.session_state.stream_buffer}
    )
    st.session_state.stream_buffer = ""  # 스트림 버퍼 초기화
markdown()