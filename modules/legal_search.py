from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
import os
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI


def load_legal_knowledge_base(api_key: str):
    with open("data/saudi_labor_laws.txt", "r") as f:
        raw_text = f.read()

   #splits text/things into chunks
    splitter = CharacterTextSplitter(separator="\n", chunk_size=300, chunk_overlap=20)
    docs = splitter.create_documents([raw_text])

    # creates  embeddings
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore

def answer_question_from_lawbase(question: str, vectorstore, api_key: str) -> str:
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)  # type: ignore
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )
    result = qa_chain.invoke({"query": question})
    return result["result"]

