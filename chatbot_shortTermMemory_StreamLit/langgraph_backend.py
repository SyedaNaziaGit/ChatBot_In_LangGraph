from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

load_dotenv()

llm = ChatOpenAI()

#creating state
class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    
#defining the node here
def chat_node(state:ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages':[response]}


#creating a checkpointer for the persistance- Short term memory with InMemorySavr on RAM
checkpointer = InMemorySaver()

#creating graph
graph = StateGraph(ChatState)
graph.add_node('chat_node',chat_node)
#edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

#compling grpah - to create a workflow
chatbot = graph.compile(checkpointer=checkpointer)