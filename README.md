# Multi AI Agent Newsroom 

**The Glass-Box Newsroom** is a Streamlit application that leverages **CrewAI** to orchestrate a team of autonomous AI agents. These agents collaborate to research, write, and edit high-quality blog posts on any given topic in real-time.

##  Features

- **Multi-Agent Collaboration**: A coordinated crew of AI agents working together:
  - **Senior Research Analyst**: Uncovers cutting-edge developments and trends using Tavily Search.
  - **Lead Tech Writer**: Crafts compelling, long-form narratives based on the research.
  - **Chief Editor**: Polishes the content for a professional tone and publication readiness.
- **Powered by Groq**: Utilizes the `llama-3.3-70b-versatile` model for ultra-fast and high-quality inference.
- **Live Feedback**: View agent thought processes and activities in real-time through the Streamlit UI.
- **Interactive Configuration**: Easily customize the topic and input API keys via the sidebar.

##  Technology Stack

- **[CrewAI](https://crewai.com)**: Framework for orchestrating role-playing AI agents.
- **[Streamlit](https://streamlit.io)**: Frontend interface for the application.
- **[Groq](https://groq.com)**: High-performance AI inference engine.
- **[Tavily](https://tavily.com)**: Specialized search API for AI agents.

##  Prerequisites

Before running the application, ensure you have the following API keys:
- **Groq API Key**: For the LLM.
- **Tavily API Key**: For web search capabilities.

## Installation

1. Clone the repository (if applicable) or navigate to the project directory.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:

```bash
streamlit run main.py
```

2. The application will open in your browser.
3. In the sidebar:
   - Enter your **Groq API Key**.
   - Enter your **Tavily Search Key**.
   - Enter a **Topic** you want the agents to write about (e.g., "The Future of Open Source AI").
4. Click **"Start Production"**.
5. Watch the agents work in the left column and view the final article in the right column!

## Project Structure

- `main.py`: The core application logic, including agent definitions, task setup, and Streamlit UI.
- `requirements.txt`: Python dependencies.