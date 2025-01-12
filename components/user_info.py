from components.markdown_func import markdown
import streamlit as st

def create_input(label, options, input_type, session_state_key, col, placeholder="선택해주세요..."):
    """Selectbox와 Radio 버튼을 생성하고, 값을 세션 상태에 저장"""
    markdown()  # 스타일 적용
    st.markdown(f"<p class='small-header'>{label}</p>", unsafe_allow_html=True)
    
    # 기존 선택 값이 있다면 해당 값을 기본값으로 설정
    selected_value = st.session_state.get(session_state_key, None)

    if input_type == "selectbox":
        selected_value = st.selectbox(label, options, index=None if selected_value is None else options.index(selected_value),
                                      placeholder=placeholder, label_visibility=st.session_state.visibility)
    elif input_type == "radio":
        selected_value = st.radio(label, options, index=None if selected_value is None else options.index(selected_value),
                                  label_visibility=st.session_state.visibility)
    
    st.session_state[session_state_key] = selected_value
    st.markdown(f"**선택: {selected_value}**")
    return selected_value


def user_info():
    # 결과 페이지일 때 사용자 정보 숨기기
    if st.session_state.get('result_page', False):
        return
    """사용자 정보 선택"""
    # 3개의 열을 두 개씩 생성
    cols = [st.columns(4) for _ in range(2)]
    st.session_state.visibility = "collapsed"
    
    # 입력 항목을 튜플로 정의
    inputs = [
        ("나이를 선택하세요", ["20 ~ 30세", "30 ~ 40세", "40 ~ 50세", "50 ~ 60세", "60 ~ 70세", "70세 이상"], "selectbox", "age", cols[0][0]),
        ("자차 소유 여부", ["O", "X"], "radio", "vehecle", cols[0][1]),
        ("대중교통비용/1달", ["~ 1만원", "1만원 ~ 5만원", "5만원 ~ 10만원", "10만원 ~ 50만원", "50만원 이상"], "selectbox", "pb_tras_fee", cols[0][2]),
        ("당신의 성별은?", ["남성", "여성", "기타"], "radio", "defined_sex", cols[0][3]),
        ("연회비를 선택하세요", ["~ 1만원", "1만원 ~ 5만원", "5만원 ~ 10만원", "10만원 ~ 50만원", "50만원 이상"], "selectbox", "cred_perf_y", cols[1][0]),
        ("카드실적 기준", ["10만원 이하", "10만원 ~ 20만원", "20만원 ~ 30만원", "30만원 ~ 50만원", "50만원 ~ 75만원", "150만원 이상"], "selectbox", "perf_fee", cols[1][1]),
        ("해외결제 여부", ["O", "X"], "radio", "foreign_trans", cols[1][2]),
        ("원하는 혜택 1순위", ["적립", "반려동물", "음식점/배달/카페/베이커리", "쇼핑/온라인쇼핑", "OTT/영화/공연/전시", "테마파크", "프리미엄", "피트니스/레저/스포츠", "마트/편의점", "통신요금", "주유/차량정비", "교통비", "여행/숙박", "교육/육아", "병원/약국", "공과금"],
         "selectbox", "foremost_benefit", cols[1][3])
    ]

    # 페이지가 '네' 또는 '아니오'에 따라 입력 항목을 설정
    if st.session_state.page == '네':
        inputs_to_display = inputs[:7]  # 4개의 입력 항목만 표시
    elif st.session_state.page == '아니오':
        inputs_to_display = inputs[:]  # 모든 입력 항목 표시
    else:
        inputs_to_display = []  # 기본적으로 빈 리스트로 초기화 (에러 방지)

    # 입력 항목을 표시하는 코드
    if inputs_to_display:
        for label, options, input_type, key, column in inputs_to_display:
            with column:
                create_input(label, options, input_type, key, column)
    else:
        st.error("입력 데이터가 제대로 초기화되지 않았습니다.")


        # 사용자 정보를 딕셔너리로 수집
    user_data = {
        "age": st.session_state.get("age"),
        "vehicle": st.session_state.get("vehicle"),
        "transport_fee": st.session_state.get("pb_tras_fee"),
        "gender": st.session_state.get("defined_sex"),
        "annual_fee": st.session_state.get("cred_perf_y"),
        "performance_fee": st.session_state.get("perf_fee"),
        "is_foreign": st.session_state.get("foreign_trans"),
        "foremost_benefit": st.session_state.get("foremost_benefit")
    }


    
    # st.write(user_data)

    return user_data