import streamlit as st
from components.output import output
import json
import uuid

# 세션 상태 초기화
if 'show_decision' not in st.session_state:
    st.session_state.show_decision = False

# llm_initialized 세션 상태 초기화 추가
if 'llm_initialized' not in st.session_state:
    st.session_state.llm_initialized = False

# 세션 상태 초기화 부분에 추가
if 'stream_buffer' not in st.session_state:
    st.session_state.stream_buffer = ""

# 세션 상태 초기화 부분에 추가
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 세션 상태 초기화 부분에 추가
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def decide():
    """모든 선택 사항을 확인하고 결정을 처리"""
    # 세션 상태에 결과 페이지 상태 추가
    if 'result_page' not in st.session_state:
        st.session_state.result_page = False

    # 결과 페이지 표시
    if st.session_state.result_page:
        st.empty()  # 기존 내용 지우기
        output()  # output 함수 호출

    else:
        all_selected = True
        missing_fields = []

        # 항목들을 딕셔너리로 관리
        fields = {'age': '나이', 'vehecle': '자차 소유 여부', 'pb_tras_fee': '교통비', 'defined_sex': '성별',
                  'cred_perf_y': '연회비', 'foreign_trans': '해외결제 여부', 'perf_fee': '카드 실적'}

        # 필드 검사
        for field, label in fields.items():
            if st.session_state.get(field) is None:
                missing_fields.append(label)
                all_selected = False

        # 필수 입력 항목을 체크하는 조건을 딕셔너리로 관리
        checks = [('page', '네', 'uploaded_file', '파일 업로드'),
                  ('page', '아니오', 'selected_card', '카드 선택'),
                  ('page', '아니오', 'foremost_benefit', '최우선 혜택')]

        # 각 조건을 확인하고, 필요한 항목을 추가
        for condition_key, condition_value, field_key, field_name in checks:
            if st.session_state.get(condition_key) == condition_value and st.session_state.get(field_key) is None:
                missing_fields.append(field_name)
                all_selected = False

        # 항목을 선택해야 진행할 수 있다는 알림 표시
        if not all_selected:
            st.warning(f"항목을 선택해야 결정을 진행할 수 있습니다.\n\n다음 항목을 선택해주세요: {', '.join(missing_fields)}")
        else:
             # 선택된 정보를 미리 출력
            if not st.session_state.show_decision:
                st.subheader("선택된 정보:")
                if st.session_state.page in ['네']:
                    st.write("**지출 내역본 여부**: O")
                else:
                    st.write("**지출 내역본 여부**: X")

                if st.session_state.get('page') == '네':
                    st.write(f"**나이**: {st.session_state.get('age', '선택 안함')}")
                    st.write(f"**자차 소유 여부**: {st.session_state.get('vehecle', '선택 안함')}")
                    st.write(f"**교통비**: {st.session_state.get('pb_tras_fee', '선택 안함')}")
                    st.write(f"**성별**: {st.session_state.get('defined_sex', '선택 안함')}")
                    st.write(f"**연회비**: {st.session_state.get('cred_perf_y', '선택 안함')}")
                    st.write(f"**카드 실적**: {st.session_state.get('perf_fee', '선택 안함')}")
                    st.write(f"**해외결제 여부**: {st.session_state.get('foreign_trans', '선택 안함')}")

                if st.session_state.get('page') == '아니오':
                    st.write(f"**카드사**: {st.session_state.get('selected_card', '선택 안함')}")
                    st.write(f"**나이**: {st.session_state.get('age', '선택 안함')}")
                    st.write(f"**자차 소유 여부**: {st.session_state.get('vehecle', '선택 안함')}")
                    st.write(f"**교통비**: {st.session_state.get('pb_tras_fee', '선택 안함')}")
                    st.write(f"**성별**: {st.session_state.get('defined_sex', '선택 안함')}")
                    st.write(f"**연회비**: {st.session_state.get('cred_perf_y', '선택 안함')}")
                    st.write(f"**카드 실적**: {st.session_state.get('perf_fee', '선택 안함')}")
                    st.write(f"**해외결제 여부**: {st.session_state.get('foreign_trans', '선택 안함')}")


                # 지출 정보 유무에 따른 선택된 정보
                if st.session_state.get('page') == '아니오':
                    st.write(f"**최우선 혜택**: {st.session_state.get('foremost_benefit', '선택 안함')}")


                if st.session_state.get('page') == '네':
                    selected_info = {
                        '지출 내역본 여부': 'O',
                        '나이': st.session_state.get('age', '선택 안함'),
                        '자차 소유 여부': st.session_state.get('vehecle', '선택 안함'),
                        '교통비': st.session_state.get('pb_tras_fee', '선택 안함'),
                        '성별': st.session_state.get('defined_sex', '선택 안함'),
                        '연회비': st.session_state.get('cred_perf_y', '선택 안함'),
                        '카드 실적': st.session_state.get('perf_fee', '선택 안함'),
                        '해외결제 여부': st.session_state.get('foreign_trans', '선택 안함')
                    }
                    
                if st.session_state.get('page') == '아니오': 
                    selected_info = {
                        '지출 내역본 여부': 'X',
                        '카드사': st.session_state.get('selected_card', '선택 안함'),
                        '최우선 혜택': st.session_state.get('foremost_benefit', '선택 안함'),
                        '나이': st.session_state.get('age', '선택 안함'),
                        '자차 소유 여부': st.session_state.get('vehecle', '선택 안함'),
                        '교통비': st.session_state.get('pb_tras_fee', '선택 안함'),
                        '성별': st.session_state.get('defined_sex', '선택 안함'),
                        '연회비': st.session_state.get('cred_perf_y', '선택 안함'),
                        '카드 실적': st.session_state.get('perf_fee', '선택 안함'),
                        '해외결제 여부': st.session_state.get('foreign_trans', '선택 안함')
                    }
                
            # 결정 버튼 추가
            if st.button("결정"):
                st.session_state.show_user_info = False  # 사용자 정보 숨기기
                st.session_state.show_card_selection = False  # 카드 선택 숨기기

                # 로딩 메시지 표시
                with st.spinner("답변을 생성 중입니다. 잠시만 기다려주세요..."):
                    # 필요한 데이터 처리 및 LLM 응답 생성
                    file_path = 'data/user_info_output.json'
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(selected_info, ensure_ascii=False, indent=4))
                    
                    st.success("선택된 정보가 저장되었습니다!")
                    st.session_state.result_page = True  # 결과 페이지로 이동
                    st.rerun()  # 페이지 새로고침 