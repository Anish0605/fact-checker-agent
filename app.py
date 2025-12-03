import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

# 1. Setup the Page
st.set_page_config(page_title="AI Fact Checker", page_icon="🕵️")
st.title("🕵️ Instant Fact Checker Agent")

# 2. Get the API Key from Secrets (we set this up in Step 3)
api_key = st.secrets["GROQ_API_KEY"]

if not api_key:
    st.error("API Key not found!")
    st.stop()

client = Groq(api_key=api_key)

# 3. Define the "Search" Tool
def search_web(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
        if results:
            return "\n".join([f"- {r['title']}: {r['body']} ({r['href']})" for r in results])
        return "No results found."

# 4. The User Interface
user_query = st.text_input("Enter a claim to verify:", placeholder="e.g., Did Apple stock go up today?")

if user_query:
    with st.spinner("Searching the web..."):
        # Step A: Search for facts
        search_results = search_web(user_query)
        
        # Step B: Let the AI analyze the facts
        prompt = f"""
        You are a professional Fact Checker. 
        Here is the user's claim: "{user_query}"
        
        Here is the evidence found online:
        {search_results}
        
        Based ONLY on this evidence, verify the claim. 
        Be concise. Cite your sources.
        """
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        
        # Step C: Show result
        st.success("Analysis Complete!")
        st.markdown(completion.choices[0].message.content)
