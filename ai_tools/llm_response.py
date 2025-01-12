import streamlit as st
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_community.vectorstores import Pinecone
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from dotenv import load_dotenv

# 전역 변수 선언
llm = None
embeddings = None
load_vec_db = None
store = {}

def initialize_llm():
    """LLM, Embeddings, Vector DB를 초기화하는 함수"""
    global llm, embeddings, load_vec_db
    
    if llm is not None and embeddings is not None and load_vec_db is not None:
        return

    load_dotenv()
    
    llm = ChatUpstage(model='solar-pro')
    embeddings = UpstageEmbeddings(model='embedding-query')
    load_vec_db = Pinecone.from_existing_index(
        index_name='sesac-card-project',
        embedding=embeddings
    )

def get_retriever(is_first_message=False):
    """검색기 설정"""
    global load_vec_db
    if load_vec_db is None:
        initialize_llm()

    retriever = load_vec_db.as_retriever(search_kwargs={"k": 2 if is_first_message else 1})
    return retriever

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """세션 히스토리 관리 함수"""
    global store
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    
    chat_history = store[session_id]
    chat_history.clear()
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_history.add_user_message(msg["content"])
        elif msg["role"] == "assistant":
            chat_history.add_ai_message(msg["content"])

    return chat_history

def get_history_chain():
    llm = ChatUpstage(model = 'solar-pro')
    retriever = get_retriever()
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever

def get_qa_chain(prompt_flag=False):
    """QA 체인 생성 함수"""
    # 필요할 때만 임포트
    from ai_tools.example import answer_examples
    from langchain_core.prompts import FewShotChatMessagePromptTemplate
    
    # LLM 초기화는 한 번만 수행하도록 변경
    global llm
    if llm is None:
        llm = ChatUpstage(model='solar-pro')

    history_aware_retriever = get_history_chain()
    
    with_excel_prompt = SystemMessagePromptTemplate.from_template("""
     당신은 다음 context를 기반으로 가장 적절한 신용카드를 추천하는 전문가입니다.
     
     먼저, [지출 내역]이 있는 경우, 분석하여 사용자의 소비 패턴과 특징을 파악해주세요.
    
    ### **주의 사항**:
    - 제공된 데이터만 사용하고, 주의 깊게 읽고 이해합니다. **가정이나 추정, 생략 및 왜곡은 금지입니다.**
    - 예시는 어디까지나 예시입니다. 예시를 그대로 이용하려하지 마세요.
    - **오직 최신 업로드 파일만 사용**하세요. 이전 파일 및 이전 데이터들은 절대 사용하지 마세요. 이전 파일 및 이전 데이터들을 참조하거나 기억해서는 안 됩니다.
    - 분석 및 추천 결과는 **항상 제공된 파일 데이터에만 기반**해야 하며, 외부 데이터나 예시는 포함하지 마세요.
    - **너무 짧지도 너무 길지도 않게 대답**하되 요구사항에 따라 길이를 조절해주세요.
    - **혼란을 줄만한 대답은 하지 마세요**. 모르면 필요한 사항에 대해서 다시 질문을 해주세요.
    - 마치 영업사원처럼 신용카드 가입욕구를 느끼도록 부드럽게 대해주세요.
    - 카드 관련 데이터 사용 시 **pinecone DB에 저장되어 있는 데이터 기반으로만 추천합니다**.
                                                                  
    ### **분석 지침**:
     다음과 같은 내용을 포함하여 분석해주세요:
     'result'데이터의 **결제 장소, 금액, 지출카테고리**의 세 가지 데이터과 **category_ratio**, **total_amount_spent**가 있습니다. 이를 인지하고 잘 활용하세요.
     1. 반드시 **'총 지출 금액: ₩[total_amount_spent]'** 형식으로 출력해 주세요.
        **출력 시 주의 사항**:
        - **숫자 자릿수가 변경되거나 잘못된 자릿수가 추가되지 않도록** 주의하세요. 출력된 숫자는 정확히 **원래의 값을 유지**해야 합니다.
        - **금액은 반드시 정수 그대로** 출력되어야 하며, **total_amount_spent 뒤에 불필요한 0이나 소수점이 붙지 않도록** 유의하세요. **아무 이유 없이** **가장 많은 실수를 하고 있다는 점 반드시 인지** 하세요. 
        - **금액은 반점(콤마)**으로 자릿수를 구분하기 위해 **천 단위마다 반점**을 추가하여 표시해야 합니다.
                                 
     2. 반드시 **'category([category_ratio]%)'** 형식으로 출력해 주세요.
        **주의 사항**:
        - 각 **'결제 장소'**에 각 **'금액'**은 어떻게 되어있는지 잘 확인하고 왜곡 없이 일치해야 합니다.
        - **각 카테고리별 비율**은 이미 정해진 값으로 변하지 않는 부동수입니다. 임의로 변경하지 마세요.
        - 사용자가 제공한 지출 내역에 맞춰서 **동적으로 계산된 비율**을 출력하세요. 예를 들어, **식비** 카테고리가 50%일 경우, 실제 지출 데이터를 바탕으로 계산된 비율을 **식비(50%)** 형태로 출력하도록 합니다.
        - **category**는 지출카테고리 열 내의 있는 이름입니다.
        - **'결제 장소' 및 '금액' 등 길어질 수 있는 자세한 정보는 바로 출력하지 말고 사용자가 추가 질문을 할 때 한해서 그 때 답변 하세요.** 답변 대기 시간이 길어지기 때문입니다.
                                                                  
     3. 주로 어떤 업종에서 소비하는지
     4. 소비 패턴의 특징
     5. 이러한 소비 패턴을 가진 사용자의 라이프스타일 추정                                               
     6. 제공된 카드 지출 내역을 바탕으로 소비 패턴을 분석한 후, 가장 적합한 신용카드를 Pinecone DB에서만 검색하여 추천해주세요.
        **추천 시 주의 사항**:
        - **Pinecone DB에서 제공하는 카드 데이터만 반드시 사용**해야 합니다. 외부 데이터, 추측 및 임의, 상상의 카드는 절대로 사용하지 마세요.
        - 카드사명과 카드명은 반드시 **정확히 일치**해야 합니다.
        - 카드사명과 카드명은 Pinecone DB에서 제공하는 카드 데이터를 기반으로 **완전히 일치**해야 하며, 카드사의 공식 명칭을 그대로 사용해야 합니다.
        - **추천하는 카드의 혜택**은 Pinecone DB에 기록된 **정확한 혜택**을 기반으로 하여야 하며, 카드사의 공식 혜택을 그대로 참조해주세요.
        - 각 카드의 **특정 혜택**이 사용자의 소비 패턴에 얼마나 적합한지를 고려하여, 가장 적합한 카드 혜택을 중심으로 추천해주세요.
        - 카드 추천 결과는 카드사명과 카드명이 **정확히 일치**하며, 해당 카드의 **혜택**을 **구체적으로 명시**해주세요.
     
    ### **검증 요구**:
    - 계산 오류나 데이터 왜곡이 없도록 검토하고, 예시 금액이나 비율을 그대로 사용하지 마세요.
    - 최신 업로드 파일에서 제공된 데이터와 출력 결과가 **일관되도록 유지**하고, 왜곡되지 않게 응답을 작성하세요.
    - **'지출 카테고리' 및 '총 지출 금액'**는 **오직 최신 업로드 파일**을 통해서만 추출하세요.
     
    ### **컨텍스트 설명**:
     그리고 이제 너가 참조할 [context]의 json 파일의 key에 대해 각각 설명을 해줄테니 참고해주세요:
     "card_img" : 카드의 실물 사진을 담은 url입니다.
     "name": 이 제이슨 파일이 표현하는 신용카드의 공식 대표이름입니다.
     "categories" : 이 카드가 갖고있는 혜택의 목록입니다.
     "annual_fee" : 카드이용을 위해 내야하는 연 회비입니다.
     "company": 카드를 발급한 회사의 이름입니다.
     "Monthly_spending_requirement" : 혜택을 받기위한 월별 최소실적 금액이고 단위는 한국원입니다.
     "overseas_payment" : visa, mastercard 처럼 해외 결제를 가능하게 하는 서비스의 지원 여부입니다.
     
     [context]
     {context}
     [지출 내역]
     {uploaded_file_content}
     
     위의 [context]와 지출 내역을 참고해서 **리스트 형식으로 답변**해주세요:
     1. 지출 내역 분석 결과
     2. 사용자의 추정 프로필과 라이프스타일
     3. 추천하는 카드와 그 이유
     4. 혜택과 유의사항

     '지출 내역 분석 결과'과 '사용자의 추정 프로필과 라이프스타일'은 단 한번만 출력하세요.
     """)

    without_excel_prompt = SystemMessagePromptTemplate.from_template("""
     당신은 다음 context를 기반으로 가장 적절한 신용카드를 추천하는 전문가입니다.
                                                                  
     마치 영업사원처럼 신용카드 가입욕구를 느끼도록 부드럽게 대해주세요.
     
     컨텍스트를 통해서 모든 신용카드에 대해 알고 있으며 그 이외에는 고려하지 않습니다.
     항상 카드의 이름을 통해서 어떤 카드에 대해 말하고 있는지를 명시해야 합니다.
     너무 짧지도 너무 길지도 않게 대답하되 요구사항에 따라 길이를 조절해주세요.
     혼란을 줄만한 대답은 하지 마세요. 모르면 필요한 사항에 대해서 다시 질문을 해주세요.
     
     그리고 이제 너가 참조할 [context]의 json 파일의 key에 대해 각각 설명을 해줄테니 참고해주세요:
     "card_img" : 카드의 실물 사진을 담은 url입니다.
     "name": 이 제이슨 파일이 표현하는 신용카드의 공식 대표이름입니다.
     "categories" : 이 카드가 갖고있는 혜택의 목록입니다.
     "annual_fee" : 카드이용을 위해 내야하는 연 회비입니다.
     "company": 카드를 발급한 회사의 이름입니다.
     "Monthly_spending_requirement" : 혜택을 받기위한 월별 최소실적 금액이고 단위는 한국원입니다.
     "overseas_payment" : visa, mastercard 처럼 해외 결제를 가능하게 하는 서비스의 지원 여부입니다.
                                                                 
     [context]
     {context}
     
     위의 [context]를 참고해서 다음과 같은 순서로 답변해주세요:
     1. 사용자의 추정 프로필과 라이프스타일
     2. 추천하는 카드와 그 이유
     3. 혜택과 유의사항
                                                                     
     '사용자의 추정 프로필과 라이프스타일'은 단 한번만 출력하세요.
    """)

    if prompt_flag:
        qa_system_prompt = with_excel_prompt
    else:
        qa_system_prompt = without_excel_prompt

    example_prompt = ChatPromptTemplate.from_messages([('human', '{input}'), ('ai', '{answer}')])
    
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        examples=answer_examples,
        example_prompt=example_prompt,
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            qa_system_prompt,
            few_shot_prompt,
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    # 질문-답변 체인 생성
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
        session_id_key="configurable.session_id",
    ).pick('answer')

    return conversational_rag_chain

def process_uploaded_file(uploaded_file):
    """파일 처리 함수"""
    if uploaded_file is None:
        return None
        
    # 필요할 때만 임포트
    from PyPDF2 import PdfReader
    import pandas as pd
    from components.card_spending_history import card_spending_history
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'xlsx':
            # 엑셀 파일 처리
            total_amount_spent, 카테고리_데이터 = card_spending_history(uploaded_file)
            
            categories = [
                '식비', '교통비', '주거비', '의료비', '통신비', '의류/패션',
                '취미/여가', '건강/미용', '교육비', '기부/후원', '보험료',
                '금융/투자', '세금/필수비용', '기타'
            ]
            
            # 지출 카테고리별로 금액과 비율 계산
            result = {"total_amount_spent": total_amount_spent}
            for category in categories:
                category_data = 카테고리_데이터.get(category, None)
                if category_data is not None:
                    category_total = category_data['이번달 내실금액'].sum()
                    category_ratio = (category_total / total_amount_spent) * 100
                    result[f"{category}"] = category_data.to_dict(orient="records")
                    result[f"{category}_ratio"] = category_ratio
                
            return result
        
        elif file_extension == 'pdf':
            # PDF 파일 처리
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text  # PDF에서 추출된 텍스트 반환
            
    except Exception as e:
        st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
        return None

def get_llm_response(user_input, session_id, filter=None):
    """LLM 응답 처리 함수"""
    global llm
    if llm is None:
        initialize_llm()
    
    prompt_flag = False
    file_content = None
    
    # 첫 메시지 여부 확인
    is_first_message = len(st.session_state.messages) <= 1

    # 업로드된 파일이 있으면 처리
    uploaded_file_content = st.session_state.get('uploaded_file', None)
    has_file = uploaded_file_content is not None
    
    if has_file:
        file_content = process_uploaded_file(uploaded_file_content)
        prompt_flag = True

    # 파일이 텍스트인 경우 (PDF 파일)
    if isinstance(file_content, str):
        file_content_text = file_content
        
        retriever = get_retriever(is_first_message=is_first_message)
        qa_retriever = get_qa_chain(prompt_flag=prompt_flag)

        search_results = retriever.invoke(user_input)

        for chunk in qa_retriever.stream(
            {"input": user_input, 'context': search_results, 
             'uploaded_file_content': file_content_text, 
             "session_id": session_id},
            config={"configurable": {"session_id": session_id}}
        ):
            yield chunk

    # 파일이 엑셀인 경우
    elif isinstance(file_content, dict):
        import pandas as pd
        # 데이터가 pandas DataFrame이면 리스트로 변환하는 보조 함수
        def process_expenses(expenses):
            if isinstance(expenses, pd.DataFrame):
                return expenses.to_dict(orient="records")
            return expenses
        
        result = {}
        if file_content:
            total_amount_spent = file_content.get('total_amount_spent')
            for category in ['food_expenses', 'transportation_expenses', 'housing_expenses', 'medical_expenses',
                             'communication_cost', 'clothing_expenses', 'hobby_fee', 'health_expenses',
                             'education_expenses', 'donation', 'insurance_premiums', 'finance', 'duty', 'etc']:
                category_data = process_expenses(file_content.get(category))
                category_ratio = file_content.get(f"{category}_ratio", None)
                result[category] = category_data
                if category_ratio is not None:
                    result[f"{category}_ratio"] = category_ratio
            
            retriever = get_retriever(is_first_message=is_first_message)
            qa_retriever = get_qa_chain(prompt_flag=prompt_flag)
            
            search_results = retriever.invoke(user_input)
            
            for chunk in qa_retriever.stream(
                {"input": user_input, 'context': search_results,
                 'uploaded_file_content': file_content,
                 "total_amount_spent": total_amount_spent, # 총 지출 금액 정보 추가
                 **result},  # 카테고리 데이터를 통합하여 전달
                config={"configurable": {"session_id": session_id}}  # config에 session_id 추가
            ):
                yield chunk

    # 파일이 없을 경우
    else:
        retriever = get_retriever(is_first_message=is_first_message)
        qa_retriever = get_qa_chain(prompt_flag=prompt_flag)

        search_results = retriever.invoke(user_input)

        for chunk in qa_retriever.stream(
            {"input": user_input, 'context': search_results,
             'uploaded_file_content': file_content},
            config={"session_id": session_id},
        ):
            yield chunk