# modules/draft_generator.py

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from typing import Optional

def generate_legal_draft(draft_type: str, inputs: dict, api_key: Optional[str] = None) -> str:
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.4)  # type: ignore

    base_prompt = f"""
You are a legal assistant. Your task is to draft a {draft_type} using the information provided.

Details:
- Your Company Name: {inputs.get('company-name')}
- Your Company Address: {inputs.get('company-address')}
- City: {inputs.get('city')}
- State: {inputs.get('state')}
- Zip Code: {inputs.get('zip-code')}
- Email Address: {inputs.get('email-address')}
- Phone Number: {inputs.get('phone-number')}
- Date: {inputs.get('date')}
- Client Name: {inputs.get('client_name')}
- Client's Address: {inputs.get('client-address')}
- Your Name: {inputs.get('name')}
- Your Position: {inputs.get('position')}
- Opposing Party: {inputs.get('opposing_party')}
- Reason for Draft: {inputs.get('reason')}
- Jurisdiction: {inputs.get('jurisdiction', 'Saudi Arabia')}

Ensure the tone is professional and compliant with Saudi labor law. Format the output as a complete, formal legal draft.
"""

    response = llm([HumanMessage(content=base_prompt)])
    return response.content 