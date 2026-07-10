from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage,HumanMessage
#from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt  import ToolNode,tools_condition
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import requests

#loading env vars
load_dotenv()

#1. LLM Here
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
#llm = ChatOpenAI()

#2. Tools Here
#builtinn tool
search_tool = DuckDuckGoSearchRun()
search_tool = DuckDuckGoSearchRun()

#custom tool using decorator
@tool
def calculator(firstnum:float,secondnum:float,operation:str):
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = firstnum + secondnum
        elif operation == "sub":
            result = firstnum - secondnum
        elif operation == "mul":
            result = firstnum * secondnum
        elif operation == "div":
            result = firstnum/secondnum
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        return {"first_num": firstnum, "second_num": secondnum, "operation": operation, "result": result}
    except Exception as e:
        return {"error":str(e)}

#third tool to get the stock 
@tool
def get_stock_price(symbol:str):
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    response = requests.get(url=url)
    return response.json()

#Making tool node and binding it
tools = [search_tool,calculator,get_stock_price]
llm_with_tools = llm.bind_tools(tools)

#3 Defining State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

#creatinga DB checkpointer
# Checkpointer
conn = sqlite3.connect(database="chatbot.db",check_same_thread=False)
checkpointer = SqliteSaver(conn= conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools",tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges('chat_node',tools_condition)
graph.add_edge('tools', 'chat_node')
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)