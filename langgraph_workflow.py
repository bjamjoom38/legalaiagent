"""
LangGraph Workflow for Legal Document Assistant
Implements an AI agent engine with smart routing and autonomous decision-making
"""

from typing import TypedDict, List, Dict, Any, Optional, cast
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from pydantic import SecretStr

# Import custom modules
from modules.analyze_doc import analyze_text_with_openai
from modules.legal_search import load_legal_knowledge_base

# Load environment variables
load_dotenv()

class AgentState(TypedDict):
    """State schema for the legal agent workflow"""
    input: str
    legal_text: str
    intent: str
    output: str
    vectorstore: Any

class LegalAgentWorkflow:
    """Legal document assistant powered by LangGraph"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=SecretStr(self.api_key),
            model="gpt-4",
            temperature=0.1
        )
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
    def _build_workflow(self):
        """Build the LangGraph workflow with routing logic"""
        
        # Define the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("summarize", self._summarize_document)
        workflow.add_node("legal_qa", self._answer_legal_question)
        workflow.add_node("draft_document", self._draft_document)
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "classify_intent",
            self._route_based_on_intent,
            {
                "summarize": "summarize",
                "legal_question": "legal_qa",
                "draft_request": "draft_document"
            }
        )
        
        # Add edges to END
        workflow.add_edge("summarize", END)
        workflow.add_edge("legal_qa", END)
        workflow.add_edge("draft_document", END)
        
        return workflow.compile()
    
    def _classify_intent(self, state: AgentState) -> AgentState:
        """Classify user intent using LLM"""
        
        classification_prompt = f"""
        Analyze the following user request and classify it into one of these categories:
        - "summarize": User wants a summary or analysis of a document
        - "legal_question": User is asking a legal question that needs research
        - "draft_request": User wants to draft or generate a legal document
        
        User request: "{state['input']}"
        
        Respond with only the classification category (summarize, legal_question, or draft_request).
        """
        
        messages = [SystemMessage(content=classification_prompt)]
        response = self.llm.invoke(messages)
        
        # Handle response as list of dicts or strings robustly
        intent = None
        if isinstance(response, list):
            first = response[0]
            if isinstance(first, dict) and "content" in first:
                intent = str(first["content"]).strip().lower()
            elif hasattr(first, "content") and not isinstance(first, dict):
                intent = str(first.content).strip().lower()
            elif isinstance(first, str):
                intent = first.strip().lower()
            else:
                intent = str(first).strip().lower()
        elif hasattr(response, "content") and not isinstance(response, dict):
            intent = str(response.content).strip().lower()
        elif isinstance(response, str):
            intent = response.strip().lower()
        else:
            intent = str(response).strip().lower()
        if not intent:
            intent = "legal_question"
        
        # Ensure valid intent
        if intent not in ["summarize", "legal_question", "draft_request"]:
            intent = "legal_question"  # Default fallback
        
        state["intent"] = intent
        return state
    
    def _route_based_on_intent(self, state: AgentState) -> str:
        """Route to appropriate node based on classified intent"""
        return state["intent"]
    
    def _summarize_document(self, state: AgentState) -> AgentState:
        """Summarize legal document using existing function"""
        
        legal_text = state.get("legal_text", "")
        
        if not legal_text:
            state["output"] = "❌ No document text provided for summarization."
            return state
        
        try:
            # Use existing analyze function
            summary = analyze_text_with_openai(legal_text, str(self.api_key))
            print(f"📄 Debug - Summary result: {summary}")
            
            # Add fallback if summary is None or empty
            if not summary:
                state["output"] = "⚠️ I couldn't generate a summary for this document."
            else:
                state["output"] = f"📄 **Document Summary:**\n\n{summary}"
        except Exception as e:
            print(f"❌ Debug - Error in _summarize_document: {str(e)}")
            state["output"] = f"❌ Error summarizing document: {str(e)}"
        
        return state
    
    def _answer_legal_question(self, state: AgentState) -> AgentState:
        """Answer legal questions using RAG with legal knowledge base"""
        
        try:
            # Load legal knowledge base if not already loaded
            if "vectorstore" not in state or state["vectorstore"] is None:
                vectorstore = load_legal_knowledge_base(str(self.api_key))
                state["vectorstore"] = vectorstore
            else:
                vectorstore = state["vectorstore"]
            
            # Create RetrievalQA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            # Get answer
            result = qa_chain({"query": state["input"]})
            answer = result["result"]
            print(f"⚖️ Debug - QA result: {answer}")
            
            # Add fallback if answer is None or empty
            if not answer:
                state["output"] = "⚠️ I couldn't find an answer to your legal question."
                return state
            
            # Format response with sources
            sources = [doc.metadata.get("source", "Unknown") for doc in result["source_documents"]]
            sources_text = "\n".join([f"• {source}" for source in set(sources)])
            
            state["output"] = f"⚖️ **Legal Analysis:**\n\n{answer}\n\n**Sources:**\n{sources_text}"
            
        except Exception as e:
            print(f"❌ Debug - Error in _answer_legal_question: {str(e)}")
            state["output"] = f"❌ Error processing legal question: {str(e)}"
        
        return state
    
    def _draft_document(self, state: AgentState) -> AgentState:
        """Draft legal document (placeholder for future implementation)"""
        
        print(f"📄 Debug - Draft request: {state['input']}")
        
        try:
            output = f"📄 **Draft Generation:**\n\nDraft generation feature coming soon!\n\nYour request: \"{state['input']}\"\n\nThis will include:\n• Document template selection\n• AI-powered clause generation\n• Legal compliance checking\n• Professional formatting"
            
            # Ensure output is not empty
            if not output:
                state["output"] = "⚠️ I couldn't process your document drafting request."
            else:
                state["output"] = output
        except Exception as e:
            print(f"❌ Debug - Error in _draft_document: {str(e)}")
            state["output"] = f"❌ Error processing draft request: {str(e)}"
        
        return state
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the legal agent workflow"""
        
        # Prepare initial state
        initial_state = {
            "input": input_data.get("input", ""),
            "legal_text": input_data.get("legal_text", ""),
            "intent": "",
            "output": "",
            "vectorstore": input_data.get("vectorstore", None)
        }
        
        # Run the workflow
        result = self.workflow.invoke(cast(AgentState, initial_state))
        
        return result

# Factory function for easy instantiation
def create_legal_agent(api_key: Optional[str] = None) -> LegalAgentWorkflow:
    """Create a new legal agent workflow instance"""
    return LegalAgentWorkflow(api_key)

# Example usage (commented out)
"""
# Initialize the legal agent
legal_agent = create_legal_agent()

# Example 1: Summarize a document
result = legal_agent.invoke({
    "input": "Can you summarize this document?",
    "legal_text": "This is a sample contract between Party A and Party B..."
})
print(result["output"])

# Example 2: Ask a legal question
result = legal_agent.invoke({
    "input": "What are the key elements of a valid contract?"
})
print(result["output"])

# Example 3: Request document drafting
result = legal_agent.invoke({
    "input": "Can you help me draft a non-disclosure agreement?"
})
print(result["output"])
"""