# modules/analyze_doc.py

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

def analyze_text_with_openai(text: str, api_key: str) -> str:
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)  # type: ignore

    prompt = f"""
You are a legal assistant. The user has uploaded a legal document.
Your job is to:
- Summarize the document in simple terms
- Highlight any legal risks or unusual clauses
- Format your response in two sections:
    1. Summary
    2. Risks / Red Flags

Document:
{text[:3000]}  # Limit to 3000 characters for token safety
    """

    messages = [HumanMessage(content=prompt)]
    response = llm(messages)
    return response.content
