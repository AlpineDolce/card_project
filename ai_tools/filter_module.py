from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_community.vectorstores import Pinecone
from dotenv import load_dotenv
from langchain_upstage import UpstageEmbeddings
from langchain.chains import RetrievalQA
from langchain_upstage import UpstageEmbeddings, ChatUpstage
import re

load_dotenv()

embeddings = UpstageEmbeddings( #← OpenAIEmbeddings를 초기화
    model="embedding-query") #← 모

llm = ChatUpstage(model = 'solar-pro')
embeddings = UpstageEmbeddings(model = 'embedding-query')
load_vec_db = Pinecone.from_existing_index(
    index_name='sesac-card-project',
    embedding=embeddings
)

retriever = load_vec_db.as_retriever()

qa_retriever = RetrievalQA.from_llm(
    llm = llm,
    retriever = retriever
)



def get_annual_minmax(user_info_output): 
    annual_fee = user_info_output["연회비"]

    numbers = re.findall(r'\d+', annual_fee)
    if len(numbers) == 2:
        number_min, number_max = map(int, numbers)
    elif len(numbers) ==1:
        if numbers == 1:
            number_max = int(numbers[0])
            number_min = None
        else:
            number_min = int(numbers[0])
            number_max = None

    return number_min, number_max


def get_perform_minmax(user_info_output): 
    perform = user_info_output["카드 실적"]
    numbers = re.findall(r'\d+', perform)
    if len(numbers) == 2:
        number_min, number_max = map(int, numbers)
    elif len(numbers) ==1:
        if numbers == 10:
            number_max = int(numbers[0])
            number_min = None
        else:
            number_min = int(numbers[0])
            number_max = None
    return number_min, number_max





def get_dom_fee_range_filter(min_amount=None, max_amount=None):
    
    filter_dict = {}
    
    if min_amount is not None:
        filter_dict["domestic_fee"] = {"$gte": min_amount * 1}
    
    if max_amount is not None:
        filter_dict["domestic_fee"] = {"$lte": max_amount * 1}
    
    if min_amount is not None and max_amount is not None:
        filter_dict["domestic_fee"] = {
            "$gte": min_amount * 10000,
            "$lte": max_amount * 10000
        }
    
    return filter_dict



def get_overseas_fee_range_filter(min_amount=None, max_amount=None):
    
    filter_dict = {}
    
    if min_amount is not None:
        filter_dict["overseas_fee"] = {"$gte": min_amount * 1}
    
    if max_amount is not None:
        filter_dict["overseas_fee"] = {"$lte": max_amount * 1}
    
    if min_amount is not None and max_amount is not None:
        filter_dict["overseas_fee"] = {
            "$gte": min_amount * 10000,
            "$lte": max_amount * 10000
        }
    
    return filter_dict



# 해외결제여부
def get_overseas_payment_filter(is_overseas_usable=None):
    """
    해외 결제 여부에 따른 필터 딕셔너리 생성
    
    Args:
        is_overseas_usable (bool, optional): 해외 결제 가능 여부 (True 또는 False)
    
    Returns:
        dict: Pinecone 필터링에 사용할 딕셔너리
    """
    filter_dict = {}
    
    if is_overseas_usable is not None:
        filter_dict["is_overseas_usable"] = is_overseas_usable
    
    return filter_dict



def get_overseas_perform_filter(min_amount=None, max_amount=None):
    
    filter_dict = {}
    
    if min_amount is not None:
        filter_dict["required_previous_month_spending"] = {"$gte": min_amount * 1}
    
    if max_amount is not None:
        filter_dict["required_previous_month_spending"] = {"$lte": max_amount * 1}
    
    if min_amount is not None and max_amount is not None:
        filter_dict["required_previous_month_spending"] = {
            "$gte": min_amount * 10000,
            "$lte": max_amount * 10000
        }
    
    return filter_dict



# 특정 카테고리로 필터링하는 함수
def get_benefit_category_filter(category):
    """
    혜택 카테고리에 따른 필터 딕셔너리 생성
    
    Args:
        category (str): 혜택 카테고리
    
    Returns:
        dict: Pinecone 필터링에 사용할 딕셔너리
    """
    filter_dict = {}
    
    if category is not None:
        filter_dict["benefit_categoreis"] = category
    
    return filter_dict


def get_card_company_filter(company=None):
    """
    카드 회사에 따른 필터 딕셔너리 생성
    
    Args:
        company (str, optional): 카드 회사 이름
    
    Returns:
        dict: Pinecone 필터링에 사용할 딕셔너리
    """
    filter_dict = {}
    
    if company is not None:
        filter_dict["company"] = company
    
    return filter_dict




def get_combined_filter(user_info_output):
    
    annual_min, annual_max = get_annual_minmax(user_info_output)
    perform_min, perform_max = get_perform_minmax(user_info_output)
    if user_info_output["해외결제 여부"] == "O":
        annual_fee_filter = get_overseas_fee_range_filter(min_amount=annual_min, max_amount=annual_max)
    elif user_info_output["해외결제 여부"] == "X":
        annual_fee_filter = get_dom_fee_range_filter(min_amount=annual_min, max_amount=annual_max)
    perform_filter = get_overseas_perform_filter(min_amount=perform_min, max_amount=perform_max)
    
    


    if "최우선 혜택" in user_info_output and "카드사" in user_info_output:
        benefit_category_filter = get_benefit_category_filter(user_info_output["최우선 혜택"])
        company_filter = get_card_company_filter(user_info_output["카드사"])
        if company_filter['company'] == "선택안함":
            combined_filter = {**annual_fee_filter, **perform_filter, **benefit_category_filter}
        elif company_filter['company'] != "선택안함":
            combined_filter = {**annual_fee_filter, **perform_filter, **benefit_category_filter, **company_filter }
    
    elif "최우선 혜택" in user_info_output:
        benefit_category_filter = get_benefit_category_filter(user_info_output["최우선 혜택"])
        combined_filter = {**annual_fee_filter, **perform_filter, **benefit_category_filter}

    elif "카드사" in user_info_output:
        company_filter = get_card_company_filter(user_info_output["카드사"])
        if company_filter['company'] == "선택안함":
            combined_filter = {**annual_fee_filter, **perform_filter}
        elif company_filter['company'] != "선택안함":
            combined_filter = {**annual_fee_filter, **perform_filter, **company_filter }

    elif "최우선 혜택" not in user_info_output and "카드사" not in user_info_output:
        combined_filter = {**annual_fee_filter, **perform_filter}

    
    return combined_filter