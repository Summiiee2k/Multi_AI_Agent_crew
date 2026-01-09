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

# --- UI HELPER: STREAMING TEXT ---
def stream_text(text_placeholder, text, delay=0.005):
    """Simulates typing effect for text."""
    full_text = ""
    for char in text:
        full_text += char
        text_placeholder.markdown(full_text + "▌")
        time.sleep(delay)
    text_placeholder.markdown(full_text)

# --- UI HELPER: THE CALLBACK FUNCTION ---
def step_callback(step_output, agent_name, agent_icon, log_placeholder):
    import re
    
    # Extract the thought process using Regex for robustness
    # We look for "Thought:" followed by text, until the next keyword or end of string
    raw_log = ""
    try:
        if isinstance(step_output, list):
             raw_log = step_output[0].log
        else:
             raw_log = str(step_output)
    except:
        raw_log = str(step_output)
        
    # Regex to capture content specifically after "Thought:"
    # This handles cases where .thought attribute might be missing or empty
    match = re.search(r"Thought:\s*(.*?)(?:\nAction:|\nObservation:|$)", raw_log, re.DOTALL)
    
    clean_log = ""
    if match:
        clean_log = match.group(1).strip()
    else:
        # Fallback: if no specific "Thought:" pattern, try to show the log 
        # but filter out obvious tool outputs if possible.
        # For now, if we can't find a thought, we might just show a sanitized version 
        # or nothing to strictly adhere to "only thought"
        if "Thought:" in raw_log:
             # Just in case regex failed but keyword exists
             clean_log = raw_log.split("Thought:")[-1].split("\nAction:")[0].strip()
    
    if clean_log:
        st.session_state.log_messages.append({
            "speaker": agent_name,
            "avatar": agent_icon,
            "content": clean_log
        })
        
        # Live Streaming to the UI
        with log_placeholder:
            with st.chat_message(agent_name, avatar=agent_icon):
                st.write(f"**{agent_name}**")
                stream_placeholder = st.empty()
                stream_text(stream_placeholder, clean_log)


# --- THE AGENT CREW ---
def run_newsroom(topic_input, log_placeholder):
    # Setup LLM
    llm = "groq/llama-3.3-70b-versatile"
    search_tool = TavilySearchTool()
    
    # Define agents with the callback that now accepts the placeholder
    researcher = Agent(
        role='Senior Research Analyst',
        goal='Uncover cutting-edge developments in {topic}',
        backstory="You are an expert analyst with 20 years of experience. You find facts, dates, and numbers. You ALWAYS include source URLs for your findings.",
        tools=[search_tool],
        llm=llm,
        step_callback=lambda x: step_callback(x, "🕵️ RESEARCHER", "🔎", log_placeholder) 
    )

    writer = Agent(
        role='Lead Tech Writer',
        goal='Craft compelling content on {topic}',
        backstory="You turn data into engaging stories. You write long stories and big articles. You have 20 years of experience. Use Markdown headers. You integrate citations seamlessly.",
        llm=llm,
        step_callback=lambda x: step_callback(x, "✍️ WRITER", "📝", log_placeholder) 
    )

    editor = Agent(
        role='Chief Editor',
        goal='Polish the blog post',
        backstory="You ensure the tone is professional. You ensure that the final article has a 'References' section at the bottom.",
        llm=llm,
        step_callback=lambda x: step_callback(x, "⚖️ EDITOR", "⚖️", log_placeholder)
    )

    # Define Tasks
    task1 = Task(
        description=f"Search for latest news on {topic_input}. Summarize top 5 trends. Key Requirement: Capture the source URL for every piece of information found.",
        expected_output="Very detailed summary of trends with source URLs.",
        agent=researcher
    )
    task2 = Task(
        description="Write a full blog post based on the research. It should be long and detailed. Incorporate the findings and ensure the narrative flows well.",
        expected_output="Markdown blog post.",
        agent=writer
    )
    task3 = Task(
        description="Review the post for publication. Ensure it is professional. CRITICAL: Add a 'References' or 'Citations' section at the very bottom, listing all source URLs used in the research step. Format them as a professional bibliography or list of links.",
        expected_output="Final Markdown with a Citations section at the bottom.",
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
live_feed_placeholder = col1.container(border=True)
with live_feed_placeholder:
    st.subheader("What's Happening in the Newsroom?")
    # Create a specific container for logs that we can write to nicely
    log_area = st.container()

# Right Column: The Artifact
artifact_placeholder = col2.container(border=True)
with artifact_placeholder:
    st.subheader("Your Published Article")
    final_article_area = st.empty()


# --- RE-RENDER HISTORY ---
# This ensures history is visible on re-runs (after the process finishes)
with log_area:
    for msg in st.session_state.log_messages:
        with st.chat_message(msg["speaker"], avatar=msg["avatar"]):
             st.write(f"**{msg['speaker']}**")
             st.markdown(msg["content"])
             
if st.session_state.final_article:
    final_article_area.markdown(st.session_state.final_article)
    col2.download_button("Download Article", st.session_state.final_article, "article.md")


# --- RUN BUTTON ---
if st.sidebar.button("Start  Production"):
    if not (groq_key and tavily_key):
        st.error("Please enter keys!")
        st.stop()
        
    # Clear previous state
    st.session_state.log_messages = []
    st.session_state.final_article = ""
    # Clear the UI areas visually for this run
    log_area.empty()
    final_article_area.empty()
    
    # Display Topic
    st.markdown(f"### Current Topic: {topic}")
    
    with st.spinner("Agents are collaborating..."):
        # We pass the 'log_area' container to the function so it can write live updates
        result = run_newsroom(topic, log_area)
        
        # Simulating streaming for the final artifact as well
        final_text = str(result)
        st.session_state.final_article = final_text
        
        # Stream the final result to the right column
        stream_text(final_article_area, final_text, delay=0.002)
        
    st.success("Production Complete!")
    # No need to rerun immediately, as we've updated the UI live. 
    # But a rerun syncs everything perfectly.
    time.sleep(1)
    st.rerun()