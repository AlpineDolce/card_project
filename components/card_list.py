import streamlit as st
from components.markdown_func import markdown

# 세션 상태 초기화
if 'show_decision' not in st.session_state:
    st.session_state.show_decision = False

def card_list():  # 카드 선택 함수
    # 결과 페이지일 때 카드 선택 숨기기
    if st.session_state.get('result_page', False):
        return
    st.subheader("사용자가 원하는 혜택들을 선택하세요") 
    card_list = ['신한카드', '삼성카드', '현대카드', '우리카드', 'KB국민은행', '롯데카드', '하나카드', 'NH농협카드', 'IBK기업은행', 'BC바로카드', 
                 '애플페이', '네이버페이', '현대백화점', '카카오뱅크', '엔에이치엔페이코', '한패스', '머니트리', 'BNK경남은행', '핀크카드', '핀트', '차이', 
                 '코나카드', '토스', '씨티카드', 'MG새마을금고', 'BNK부산은행', 'DGB대구은행', '전북은행', '제주은행', '광주은행', '신협', 'Sh수협은행', 
                 'KDB산업은행', 'SBI저축은행', '카카오페이', 'SSGPAY. CARD', '유진투자증권', 'KB증권', '미래에셋증권', 'NH투자증권', '한국투자증권', 
                 'DB금융투자', 'SK증권', '유안타증권', '교보증권', 'KG모빌리언스', '트래블월렛', '다날']
    card_list.sort()
    card_list.insert(0, "선택안함")
    
    markdown()  # 스타일 적용
    st.markdown("<p class='small-header'>원하시는 카드사가 있으신가요?</p>", unsafe_allow_html=True)

    # 카드 선택 여부를 추적하기 위해 session_state에 상태 추가
    if 'selected_card' not in st.session_state:
        st.session_state.selected_card = None
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""  # 검색어 초기화
    if 'show_card_selection' not in st.session_state:
        st.session_state.show_card_selection = None  # 카드 선택 여부 초기화
    if 'card_selection' not in st.session_state:
        st.session_state.card_selection = True  # 기본적으로 카드 선택을 활성화

    # '네'와 '아니오' 버튼 생성
    col1, col2 = st.columns(2)
    with col1:
        if st.button('네'):
            st.session_state.show_card_selection = True  # 카드 선택 기능을 활성화
            st.session_state.card_selection = True  # 카드 선택을 활성화
            st.session_state.selected_card = None  # Reset selection when switching to "네"
    with col2:
        if st.button('아니오'):
            st.session_state.selected_card = '선택안함'
            st.session_state.show_card_selection = False  # 카드 선택을 하지 않음
            st.session_state.card_selection = False  # 카드 선택을 비활성화
    
    # 카드 선택 기능 활성화
    if st.session_state.show_card_selection == True:
        st.markdown("<p class='small-header'>원하시는 카드를 검색하세요</p>", unsafe_allow_html=True)

        # 카드 검색 기능
        st.session_state.visibility = "collapsed"
        search_query = st.text_input("카드 검색", value=st.session_state.search_query, 
                                     placeholder="원하시는 카드를 검색하신 후 enter키를 누르세요...", 
                                     label_visibility=st.session_state.visibility)  # 기존 검색어 유지
        st.session_state.search_query = search_query  # 사용자가 입력한 검색어를 session_state에 저장

        # 검색어에 맞는 카드 필터링
        filtered_card_list = [card for card in card_list if search_query.lower() in card.lower()]

        # 카드 목록을 감싸는 beta_expander 추가 (기본적으로 접혀 있는 상태로 설정)
        with st.expander("자세한 카드사 목록을 클릭해서 확인해보세요", expanded=bool(search_query)):  # 검색어가 있으면 자동으로 펼쳐짐
            if not filtered_card_list:
                st.write("잘못된 카드사를 입력했습니다.")  # 검색 결과가 없으면 오류 메시지 출력
            else:
                # 한 줄당 버튼 수와 총 버튼 수
                buttons_per_row = 7
                num_rows = (len(filtered_card_list) + buttons_per_row - 1) // buttons_per_row

                for row in range(num_rows):
                    row_cols = st.columns(buttons_per_row)
                    for col_idx, card in enumerate(filtered_card_list[row * buttons_per_row: (row + 1) * buttons_per_row]):
                        with row_cols[col_idx]:
                            if st.button(card, key=f"card_button_row{row}_{col_idx}") :
                                st.session_state.selected_card = card

                # 검색어에 맞는 카드가 있을 경우에만 안내 문구 출력
                st.markdown("그 중 원하시는 카드사 버튼을 클릭해주세요...")

        # 선택된 카드 표시
        if st.session_state.selected_card:
            st.markdown(f"**선택: {st.session_state.selected_card}**")

    elif st.session_state.show_card_selection == False:
        # if st.button("선택안함"):
        #     st.session_state.selected_card = '선택안함'
        # '아니오'를 클릭한 경우
        st.markdown("**카드사 선택을 안했습니다**")

    else:
        st.markdown("**카드사 선택을 해주세요**")
