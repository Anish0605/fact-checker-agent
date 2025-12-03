import streamlit as st
from groq import Groq
from tavily import TavilyClient

# 1. Setup
st.set_page_config(page_title="AI Fact Checker", page_icon="🕵️")
st.title("🕵️ Instant Fact Checker Agent")

# 2. Get Keys
groq_key = st.secrets["GROQ_API_KEY"]
tavily_key = st.secrets["TAVILY_API_KEY"]

if not groq_key or not tavily_key:
    st.error("Missing API Keys! Please check your Secrets.")
    st.stop()

# 3. Initialize Tools
client = Groq(api_key=groq_key)
tavily = TavilyClient(api_key=tavily_key)

# 4. The Agent Logic
user_query = st.text_input("Enter a claim to verify:", placeholder="e.g., What is the weather in Chennai today?")

if user_query:
    with st.spinner("🕵️‍♂️ Searching the web for live data..."):
        try:
            # Step A: Search with Tavily (The "Professional" Eyes)
            search_response = tavily.search(query=user_query, max_results=3)
            
            # Extract just the useful text from results
            results = []
            for result in search_response['results']:
                results.append(f"- {result['title']}: {result['content']} ({result['url']})")
            context = "\n".join(results)
            
            # Step B: Analyze with Groq (The "Brain")
            prompt = f"""
            You are an expert Fact Checker. 
            User Claim: "{user_query}"
            
            Verified Search Results:
            {context}
            
            Task: Answer the user's question or verify their claim based ONLY on the search results above.
            If the answer is not in the results, say "I couldn't find current info on that."
            Include links to the sources.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            
            st.success("Analysis Complete!")
            st.markdown(completion.choices[0].message.content)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
