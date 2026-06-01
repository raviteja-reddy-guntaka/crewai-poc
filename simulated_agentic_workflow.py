import time

# =================================================================
# 📚 1. VECTOR DATABASE SERVICE (Simulated ChromaDB/Pinecone)
# Responsible for turning a question into a search query.
# =================================================================
class VectorStoreClient:
    """
    Simulates interaction with a vector database (e.g., ChromaDB, Pinecone).
    Stores and retrieves relevant context based on a query.
    """
    def __init__(self, documents):
        self.documents = documents
        print(f"\n[VectorStore]: Initialized with {len(documents)} documents.")

    def embed_and_store(self, documents):
        """Simulates embedding and indexing the knowledge base."""
        # In reality, we call a model like OpenAI's text-embedding-ada-002 here.
        print("[VectorStore]: Knowledge Base indexed successfully. Ready for queries.")

    def query(self, user_query: str, top_k: int = 3) -> str:
        """
        Simulates:
        1. Embedding the user_query into a vector.
        2. Querying the vector store for the K most similar documents.
        3. Returning the raw text context.
        """
        print(f"\n[VectorStore]: 🔎 Searching knowledge base for query: '{user_query}'...")
        time.sleep(0.5) 
        
        # --- Simulated Retrieval Logic ---
        if "history" in user_query.lower():
            relevant_context = (
                "The company's founding date was January 15, 1998. "
                "The Q3 2023 financial report showed a 15% growth in market share. "
                "The CEO announced that the next product line will focus on AI integration by Q1 2024."
            )
            print("[VectorStore]: ✅ Context retrieved.")
            return relevant_context
        elif "remote" in user_query.lower():
            return "The recent company policy states that all employees can work remotely up to two days per week."
        else:
            return "No specific context found."
        

# =================================================================
# 🧠 2. LANGUAGE MODEL SERVICE (Simulated GPT-4/Gemini)
# Responsible for synthesizing the answer based on context.
# =================================================================
def call_llm_api(prompt: str, system_message: str) -> str:
    """
    Simulates calling an external LLM API (e.g., OpenAI ChatCompletion).
    The prompt contains the context and the user's question.
    """
    print("\n[LLM Service]: 💬 Calling the LLM API to synthesize the answer...")
    time.sleep(1.0) # Simulate the network latency of the API call
    
    # --- Simulated Synthesis Logic ---
    if "history" in prompt and "Q3 2023" in prompt:
        return (
            "Based on the retrieved context, the company was founded on January 15, 1998. "
            "It experienced robust growth, showing a 15% increase in market share during Q3 2023. "
            "The strategic focus moving forward, as announced by the CEO, is the integration of AI technology in Q1 2024."
        )
    
    if "remote work" in prompt and "Tuesday and Thursday" in prompt:
        return (
            "According to our HR policy, employees have the flexibility of a 3-day work week. "
            "The required mandatory in-office collaboration days are Tuesday and Thursday, ensuring key team presence."
        )
        
    return "I analyzed the prompt, but the specific context was insufficient to provide a detailed, synthesized answer."


# --- (The setup code you just ran goes here) ---

# --- START OF QUERY LOGIC ---

def answer_question(question):
    """Simulates the RAG process: Retrieve context and generate an answer."""
    print(f"\n===================================================")
    print(f"QUERY: {question}")
    print(f"---------------------------------------------------")
    
    # 1. Simulate Retrieval (The model searches the index)
    # In a real system, this function would query a vector database.
    # For this simulation, we'll use a simple context check.
    if "policies" in question.lower() or "annual leave" in question.lower():
        context = "According to the HR handbook, employees are entitled to 20 days of paid annual leave per year, which must be scheduled with manager approval."
        print(f"[RETRIEVED CONTEXT]: {context}")
    elif "payroll" in question.lower() or "salary cycle" in question.lower():
        context = "The payroll department processes salaries bi-weekly on Friday, ensuring timely disbursement to all employees."
        print(f"[RETRIEVED CONTEXT]: {context}")
    elif "office hours" in question.lower() or "remote work" in question.lower():
        context = "Standard office hours are Monday to Friday, 9 AM to 5 PM. Remote work requires manager pre-approval."
        print(f"[RETRIEVED CONTEXT]: {context}")
    else:
        context = "No specific information found in the company documents."
        print(f"[RETRIEVED CONTEXT]: {context}")

    # 2. Simulate Generation (The model writes the final answer based on context)
    if "policies" in question.lower() or "annual leave" in question.lower():
        answer = "Employees are entitled to 20 days of paid annual leave per year, but this leave must be scheduled with manager approval."
    elif "payroll" in question.lower() or "salary cycle" in question.lower():
        answer = "The payroll department processes salaries bi-weekly, with the disbursement occurring every Friday."
    elif "office hours" in question.lower() or "remote work" in question.lower():
        answer = "Standard office hours are 9 AM to 5 PM, Monday to Friday. If you plan to work remotely, you must obtain pre-approval from your manager."
    else:
        answer = "I found no specific documents related to that query."
    
    print(f"\n[GENERATED ANSWER]: {answer}")
    print("===================================================")


# --- MOCK DATABASE FUNCTION ---
def connect_to_db(db_name):
    """
    MOCK FUNCTION: This simulates establishing a database connection 
    without actually connecting. Use this until you implement real DB logic.
    """
    print(f"\n[INFO] Successfully mocked connection to database: {db_name}")
    # Instead of a real connection object, return a dummy object
    return "MockConnectionObject" 
# -----------------------------



def setup_vector_store_client(docs):
    try:
        # Connection attempt that fails silently
        connection = connect_to_db(docs) 
        if connection:
            return VectorStoreClient(connection) # This is the successful return
        # ERROR: If connection is None, nothing is returned, thus the function returns None
    except Exception as e:
        print(f"An error occurred: {e}")
        # CRITICAL: You are doing nothing here. The function ends and returns None.


# =================================================================
# 🧠 3. ORCHESTRATOR (The Brain)
# Responsible for managing the flow of data: Query -> Retrieve -> Synthesize.
# =================================================================
class RAGPipeline:
    """The central controller that coordinates all services."""
    def __init__(self, vector_store: VectorStoreClient):
        self.vector_store = vector_store

    def answer_query(self, user_query: str) -> str:
        """Executes the Retrieval-Augmented Generation flow."""
        
        # 1. RETRIEVAL STEP
        # Query the vector store to get contextual documents.
        context = self.vector_store.query(user_query)
        
        # 2. SYNTHESIS STEP (Prompt Engineering)
        # Create the system prompt that guides the LLM's behavior.
        system_message = (
            "You are an expert corporate assistant. Your sole purpose is to answer "
            "the user's question STRICTLY using the provided context. If the context "
            "does not contain the answer, you MUST say, 'I cannot find this information in the knowledge base.' "
            "Do not use external knowledge."
        )
        
        # Combine the context and the original query into the full prompt.
        full_prompt = (
            f"CONTEXT:\n---\n{context}\n---\n\n"
            f"USER QUESTION: {user_query}\n\n"
            f"TASK: Synthesize a clear, comprehensive answer based ONLY on the CONTEXT provided."
        )
        
        # 3. GENERATION STEP
        final_answer = call_llm_api(full_prompt, system_message)
        
        return final_answer

# =================================================================
# 🛠️ MAIN EXECUTION
# =================================================================
if __name__ == "__main__":
    
    # --- SETUP KNOWLEDGE BASE ---
    # These are the raw, internal documents available to the company.
    KNOWLEDGE_BASE_DOCUMENTS = [
        "The company's founding date was January 15, 1998. Key milestones include the 2005 product launch.",
        "The Q3 2023 financial report showed a 15% growth in market share, beating analyst expectations.",
        "The CEO announced that the next product line will focus on AI integration by Q1 2024.",
        "Our policy states that all employees have the option of a 3-day work week.",
        "Mandatory in-office days are Tuesday and Thursday, designed for essential team collaboration.",
        "Remote work policy allows for flexible arrangements pending manager approval.",
        "The policy on sick leave requires a doctor's note and must be submitted via the HR portal.",
        "Employees are entitled to 20 days of paid vacation leave per year.",
        "All time off requests must be submitted at least 30 days in advance for managerial approval.",
        "The operational handbook details expense reporting guidelines and reimbursement deadlines."
    ]

    # # FIX: This MUST run first. It initializes the object.
    # vector_store = setup_vector_store_client(KNOWLEDGE_BASE_DOCUMENTS) 

    # 1. Initialize Components
    vector_store = None # Not strictly needed, but good practice

    # # This MUST run second. It populates the object.
    try:
        # Your problematic setup code here
        vector_store = setup_vector_store_client(KNOWLEDGE_BASE_DOCUMENTS) 
        
    except Exception as e:
        print("\n[FATAL SETUP ERROR]: Could not initialize the Vector Store.")
        print(f"Reason: {e}")
        exit() # Stop the program if the core component fails

    # 2. Run Test Case 1 (Company History)
    query1 = "Tell me about the company's history and recent policies."
    context1 = vector_store.query(query1) # Simulate context retrieval

    # 3. Run Test Case 2 (Remote Work Policy)
    query2 = "What is the policy regarding remote work?"
    context2 = vector_store.query(query2)

    # 4. Run Test Case 3 (General Query)
    query3 = "What is the optimal way to communicate?"
    context3 = vector_store.query(query3)

    # 5. Display Results (Simulating the output flow)
    print("\n" + "="*60)
    print("                 --- TEST CASE 1: COMPANY HISTORY ---")
    print("="*60)
    print(f"Query: {query1}")
    print(f"Context Retrieved: {context1}")
    # (In a real scenario, the LLM call would happen here using context1)
    print("\n[SIMULATED LLM RESPONSE]: Based on the context, the company has achieved significant growth...")


    print("\n" + "="*60)
    print("                 --- TEST CASE 2: REMOTE WORK POLICY ---")
    print("="*60)
    print(f"Query: {query2}")
    print(f"Context Retrieved: {context2}")
    print("\n[SIMULATED LLM RESPONSE]: Based on the context, employees may work remotely up to two days per week.")


    print("\n" + "="*60)
    print("                 --- TEST CASE 3: GENERAL QUERY ---")
    print("="*60)
    print(f"Query: {query3}")
    print(f"Context Retrieved: {context3}")
    print("\n[SIMULATED LLM RESPONSE]: No specific context was found to answer this question.")

    # --- RUNNING TEST CASES ---

    # Test Case 1: Policy Query
    answer_question("What are the policies regarding annual leave?")

    # Test Case 2: Payroll Query
    answer_question("When does the company process payroll and salary cycle?")

    # Test Case 3: Remote Work Query
    answer_question("What are the current rules for office hours and remote work?")