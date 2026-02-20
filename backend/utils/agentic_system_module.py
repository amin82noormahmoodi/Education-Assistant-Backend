import os
import json

from utils.retrieval_module import FaissRetriever

from typing import Annotated, List
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.graph import StateGraph, START
from langgraph.graph import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

bachelor_faiss_path = r".\vectordb\bachelor_faiss_index"
postgraduate_faiss_path = r".\vectordb\postgraduate_faiss_index"
international_faiss_path = r".\vectordb\international_faiss_index"
ostads_faiss_path = r".\vectordb\ostads_faiss_index"
embedding_model_path = r"embedding_model"

bachelor_retriever = FaissRetriever(
    faiss_path=bachelor_faiss_path,
    model_path=embedding_model_path)

postgraduate_retriever = FaissRetriever(
    faiss_path=postgraduate_faiss_path,
    model_path=embedding_model_path)

international_retriever = FaissRetriever(
    faiss_path=international_faiss_path,
    model_path=embedding_model_path)

ostads_retriever = FaissRetriever(
    faiss_path=ostads_faiss_path,
    model_path=embedding_model_path)

with open(r"./config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

llm_model = config["GROQ_LLM_MODEL"]
api_key = config["GROQ_API_KEY"]

@tool
def bachelor_tool(query: str) -> List[str]:
    """
    Retrieve official university educational, administrative, and Kehad course information.

    This retriever searches a curated knowledge base of university regulations,
    administrative procedures, and Kehad (short-term, skill-based) course
    documentation to support RAG systems and academic information services.

    Supported topics include:
    - Admission, enrollment, and academic records
    - Educational/administrative systems (e.g., Golestan, Sajjad, military service systems)
    - Guest/transfer requests, major or field changes
    - Course registration rules, prerequisites, probation status
    - Course drop, emergency drop, term withdrawal
    - Exams, grading, graduation exams
    - Academic leave, study duration, extensions
    - Military service regulations and study exemptions
    - Withdrawal and return-to-study conditions
    - Tuition fees, free-education quotas, financial obligations
    - Academic committee decisions and educational services
    - Graduation procedures, certificates, transcripts
    - Free-education commitment cancellation and degree release
    - Official inter-organizational correspondence
    - Kehad courses: objectives, registration, target audience,
      delivery formats (in-person/online/hybrid), assessment,
      certificate issuance and validity

    Args:
        query (str): Natural-language query about educational,
            administrative, or Kehad-related information.

    Returns:
        List[str]: Up to five relevant, semantically independent
        text chunks for use in RAG or QA systems.
    """
    results = bachelor_retriever.search(query, top_k=5)
    return results

@tool
def international_tool(query: str) -> List[str]:
    """
    Retrieve authoritative information on international graduate (Master’s and PhD)
    admission and enrollment at the International Campus of Iran University of
    Science and Technology (IUST).

    This retriever covers the full admission lifecycle—from online application to
    final in-person enrollment—including procedural, academic, financial, legal,
    and administrative aspects.

    Supported topics include:
    - Step-by-step admission workflow (application → review → selection → acceptance → enrollment)
    - Applicant/staff online application systems
    - Required documents, upload rules, translations, and embassy authentication
    - Initial screening (GPA, CV quality, record completeness)
    - Faculty/department academic review
    - Interviews (requirement, scheduling, format: online/on-site, outcomes)
    - Admission decisions (with/without interview) and official admission letters
    - SAORG code acquisition and approval (Student Affairs Organization)
    - Final in-person registration procedures
    - Nationality/eligibility rules (incl. dual citizenship prohibition)
    - Academic eligibility and minimum GPA thresholds
    - Program type, structure, and duration (MSc/PhD)
    - Tuition by degree/field, payment rules, currency conversion, accepted methods
    - Persian/English requirements and remedial language courses
    - Capacity limits, CV-based scoring, prioritization
    - Violations, document discrepancies, and consequences (e.g., admission cancellation)

    Args:
        query (str): Natural-language query about international graduate admission,
            regulations, procedures, or requirements at the IUST International Campus.

    Returns:
        List[str]: Up to five relevant, authoritative, and semantically independent
        text passages addressing the query.
    """
    results = international_retriever.search(query, top_k=5)
    return results

@tool
def postgraduate_tool(query: str) -> List[str]:
    """
    Retrieve relevant information from official postgraduate (Master’s and PhD)
    regulations, bylaws, and procedural guidelines.

    This retriever searches a curated dataset of postgraduate academic policies
    and returns the most relevant document chunks based on a textual query.

    Supported topics include:
    - Academic regulations for MSc and PhD programs
    - Admission, enrollment, leave of absence, withdrawal,
    study duration (semesters) and extensions
    - Course equivalency and credit transfer policies
    - Language exam requirements, comprehensive exams,
    and academic prerequisites
    - Thesis and PhD dissertation regulations
    - Pre-defense and final defense procedures
    - Research publication rules, scientific scoring systems,
    and academic misconduct
    - Academic and administrative postgraduate procedures

    Args:
        query (str): Textual query about postgraduate regulations
            or academic policies.

    Returns:
        List[str]: Five relevant, semantically meaningful text
        chunks suitable for RAG systems.
    """
    results = postgraduate_retriever.search(query, top_k=5)
    return results

@tool
def ostads_tool(query: str) -> List[str]:
    """
    Retrieve information about faculty members of the Electrical and Computer Engineering
    departments at Iran University of Science and Technology based on a user query.

    This tool searches through a dedicated faculty knowledge base and returns the top
    5 most relevant textual results related to the given query. The retrieved information
    may include details such as faculty expertise, research interests, academic positions,
    publications, or affiliated laboratories.

    Args:
        query (str): A natural language query related to faculty members in the
            Electrical or Computer Engineering departments (e.g., professor name,
            research area, laboratory name, etc.).

    Returns:
        List[str]: A list containing 5 relevant textual results that best match
        the input query.
    """
    results = ostads_retriever.search(query, top_k=10)
    return results

llm = init_chat_model(
    llm_model,
    model_provider="groq",
    api_key=config["GROQ_API_KEY"],
    temperature=0.0)

tools = [bachelor_tool, international_tool, postgraduate_tool, ostads_tool]
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages : Annotated[list, add_messages]

def tool_calling(state:State) -> State:
    return {"messages" : llm_with_tools.invoke(state["messages"])}

builder = StateGraph(State)
builder.add_node("tool_calling_llm", tool_calling)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge("tools", "tool_calling_llm")

graph = builder.compile()

def agentic_system(query: str) -> str:
    prompt = f"""    
تو یک دستیار هوشمند آموزشی هستی که برای اداره آموزش دانشگاه علم و صنعت ایران طراحی شده‌ای و  فقط میتوانی به سوالات در مورد این دانشگاه پاسخ بدهی.
وظیفه تو پاسخ‌گویی دقیق، شفاف و مستند به پرسش‌های دانشجویان و مراجعان درباره امور آموزشی، آیین‌نامه‌ها، مقررات، فرایندهای اداری، سامانه‌های آموزشی، و دوره‌ها و برنامه‌های آموزشی (از جمله دوره‌های کهاد) است.

پاسخ‌های تو باید رسمی، محترمانه، قابل فهم و مبتنی بر اطلاعات معتبر دانشگاهی باشد. 
در صورت نبود اطلاعات قطعی یا خارج بودن سؤال از حوزه آموزش، باید با صداقت موضوع را اعلام کنی یا کاربر را به مرجع مربوطه ارجاع دهی.
از ارائه اطلاعات حدسی، غیررسمی یا خارج از اختیارات اداره آموزش خودداری کن.

این سامانه توسط امین نورمحمودی توسعه داده شده است.
پاسخ تو باید به همان زبان کاربر باشد.

سعی کن در خروجی جدول درست نکنی و بولت پوینتی ترجیحاً پاسخ بدی.

ورودی کاربر:{query}
"""
    state = {"messages" : {"messages" : prompt}}
    result = graph.invoke(state["messages"])
    return result["messages"][-1].content