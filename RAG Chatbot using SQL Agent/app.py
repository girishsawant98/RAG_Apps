import os 
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_groq import ChatGroq
from sqlalchemy import create_engine
from pathlib import Path
import sqlite3

load_dotenv()
st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

LOCAL_DB = "USE_LOCALDB"

radio_opt = ["Use SQLLite 3 Database- Employee.db"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)
db_uri = LOCAL_DB
api_key = st.sidebar.text_input(label="GRoq API Key", type="password")
if not api_key:
    st.info("Please add the groq api key")
## LLM model
llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile", streaming=True)
@st.cache_resource(ttl="2h")
def configure_db(db_uri):
    if db_uri == LOCAL_DB:
        dbfilepath = (Path(__file__).parent/"employee.db").absolute()
        if not dbfilepath.exists():
            st.error(f"Database file not found: {dbfilepath}")
            st.stop()
        print(f"Using database: {dbfilepath}")
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        try:
            db = SQLDatabase(create_engine("sqlite:///", creator=creator))
            return db
        except Exception as e:
            st.error(f"Failed to connect to database: {str(e)}")
            st.stop()

toolkit = SQLDatabaseToolkit(db=configure_db(db_uri), llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
)

# Document Chain
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input("Ask a question about the Employee database:")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        response = agent.run(user_query, callbacks=[StreamlitCallbackHandler(st.container())])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
    

