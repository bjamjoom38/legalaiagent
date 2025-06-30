import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.draft_generator import generate_legal_draft
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Draft Generator", layout="centered")
st.title("📄 Legal Draft Generator")
st.write("Fill out the form below to generate a legal draft.")

with st.form("draft_form"):
    draft_type = st.selectbox("Document Type", ["Cease and Desist", "Legal Notice", "Employment Agreement", "Service Contract"])
    
    st.subheader("🏢 Company Info")
    company_name = st.text_input("Your Company Name")
    company_address = st.text_input("Your Company Address")
    city = st.text_input("City")
    state = st.text_input("State")
    zip_code = st.text_input("Zip Code")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    date = st.date_input("Date")

    st.subheader("👤 Client & Legal Info")
    client_name = st.text_input("Client Name")
    client_address = st.text_input("Client Address")
    your_name = st.text_input("Your Name")
    position = st.text_input("Your Position")
    opposing_party = st.text_input("Opposing Party")
    reason = st.text_area("Reason for Draft")
    jurisdiction = st.text_input("Jurisdiction", value="Saudi Arabia")

    submitted = st.form_submit_button("Generate Draft")

if submitted:
    inputs = {
        "company-name": company_name,
        "company-address": company_address,
        "city": city,
        "state": state,
        "zip-code": zip_code,
        "email-address": email,
        "phone-number": phone,
        "date": str(date),
        "client_name": client_name,
        "client-address": client_address,
        "name": your_name,
        "position": position,
        "opposing_party": opposing_party,
        "reason": reason,
        "jurisdiction": jurisdiction,
    }

    with st.spinner("Generating draft..."):
        draft = generate_legal_draft(draft_type, inputs, api_key)
        st.success("✅ Draft generated!")
        st.markdown("### 📝 Legal Draft Output")
        st.code(draft, language="markdown")
