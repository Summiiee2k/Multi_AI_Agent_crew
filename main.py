import streamlit as st
import os
import time
from crewai import Agent, Task, Crew, Process
from crewai_tools import TavilySearchTool 
from langchain_groq import ChatGroq

# --- CONFIGURATION ---
os.environ["CREWAI_TRACING_ENABLED"] = "0" 

st.set_page_config(page_title="Newsroom Live", layout="wide")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stChatMessage { margin-bottom: 10px; }
    .stSpinner { margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("The Glass-Box Newsroom")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Control Panel")
    topic = st.text_input("Topic", "The Future of Open Source AI")
    
    st.markdown("### API Keys")
    groq_key = st.text_input("Groq API Key", type="password")
    tavily_key = st.text_input("Tavily Search Key", type="password")
    
    if groq_key: os.environ["GROQ_API_KEY"] = groq_key
    if tavily_key: os.environ["TAVILY_API_KEY"] = tavily_key
    os.environ["OPENAI_API_KEY"] = "NA" 

# --- SESSION STATE ---
if "log_messages" not in st.session_state:
    st.session_state.log_messages = []
if "final_article" not in st.session_state:
    st.session_state.final_article = ""

# --- UI HELPER: THE CALLBACK FUNCTION ---
# This function runs every time an agent takes a "Step" (thinks or acts)
def step_callback(step_output, agent_name, agent_icon):
    # Extract the thought process
    thought = ""
    try:
        if isinstance(step_output, list):
             thought = step_output[0].log
        else:
             thought = str(step_output)
    except:
        thought = str(step_output)
    
    # Add to Session State
    clean_log = thought.replace("Thought:", "").strip()
    if clean_log:
        st.session_state.log_messages.append({
            "speaker": agent_name,
            "avatar": agent_icon,
            "content": clean_log
        })

# --- THE AGENT CREW ---
def run_newsroom(topic_input):
    # Setup LLM
    llm = "groq/llama-3.3-70b-versatile"
    search_tool = TavilySearchTool()
    
    
    researcher = Agent(
        role='Senior Research Analyst',
        goal='Uncover cutting-edge developments in {topic}',
        backstory="You are an expert analyst with 20 years of experience. You find facts, dates, and numbers.",
        tools=[search_tool],
        llm=llm,
        step_callback=lambda x: step_callback(x, "🕵️ RESEARCHER", "🔎") 
    )

    writer = Agent(
        role='Lead Tech Writer',
        goal='Craft compelling content on {topic}',
        backstory="You turn data into engaging stories. You write long stories and big articles. You have 20 years of experience. Use Markdown headers.",
        llm=llm,
        step_callback=lambda x: step_callback(x, "✍️ WRITER", "📝") 
    )

    editor = Agent(
        role='Chief Editor',
        goal='Polish the blog post',
        backstory="You ensure the tone is professional.",
        llm=llm,
        step_callback=lambda x: step_callback(x, "⚖️ EDITOR", "⚖️")
    )

    # Define Tasks
    task1 = Task(
        description=f"Search for latest news on {topic_input}. Summarize top 5 trends.",
        expected_output="Very detailed summary of trends.",
        agent=researcher
    )
    task2 = Task(
        description="Write a full blog post based on the research. It should be long and detailed.",
        expected_output="Markdown blog post.",
        agent=writer
    )
    task3 = Task(
        description="Review the post for publication.",
        expected_output="Final Markdown.",
        agent=editor
    )

    # Run Crew
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[task1, task2, task3],
        process=Process.sequential,
        verbose=True
    )
    
    return crew.kickoff()

# --- MAIN UI LAYOUT ---
col1, col2 = st.columns([1, 1])

# Left Column: The Live Feed
with col1:
    st.subheader("What 's Happening in the Newsroom?")
    chat_container = st.container(border=True)
    
    # Render logs from history
    with chat_container:
        for msg in st.session_state.log_messages:
            with st.chat_message(msg["speaker"], avatar=msg["avatar"]):
                st.markdown(msg["content"])

# Right Column: The Artifact
with col2:
    st.subheader("Your Published Article")
    chat_container = st.container(border=True)
    with chat_container:
        if st.session_state.final_article:
            st.markdown(st.session_state.final_article)
            st.download_button("Download Article", st.session_state.final_article, "article.md")

# --- RUN BUTTON ---
if st.sidebar.button("Start  Production"):
    if not (groq_key and tavily_key):
        st.error("Please enter keys!")
        st.stop()
        
    st.session_state.log_messages = []
    st.session_state.final_article = ""
    
    with st.spinner("Agents are collaborating..."):
        result = run_newsroom(topic)
        st.session_state.final_article = str(result)
        st.rerun()