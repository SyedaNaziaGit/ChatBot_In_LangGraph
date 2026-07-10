#adding threading concept here
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage,ToolMessage
import uuid
#to generate new thread everytime uniwue so using uuid

#***************************Utility Functions Here *****************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

#new chat to get the new chat window
def reset_chat():
    #generate new threadid for new chat
    thread_id = generate_thread_id()
    #store in session 
    st.session_state['thread_id'] = thread_id
    #adding threadid to the session chatthread list
    add_threads(thread_id)
    #empty the message history of previous messgae
    st.session_state['message_history'] = []
    
#adding threadids to session thread list
def add_threads(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

#get chat history for threadid
def load_conversation(thread_id):
    return chatbot.get_state(config= {'configurable': {'thread_id': thread_id}}).values["messages"]

#generating thread_title 
def generate_thread_title(user_message,ai_response):
    title_prompt = [
        SystemMessage(content="You are a system utility. Generate an extremely short, 3-to-5 word descriptive title for a chat thread based on the user's first message and the AI's response. Do not use quotes, punctuation, or extra filler text. Example: 'Python Loop Debugging' or 'Cake Recipe Ideas'."),
        HumanMessage(content=f"User said: {user_message}\nAI replied: {ai_response}")
    ]
    title_response = chatbot.invoke(title_prompt)
    return title_response.content.strip()
        
#++++++++++++++++++++session setup++++++++++++++++++++++++++++++++++

#if messagehistory is not in the current session
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
#generating dynamic threadid and adding to session
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()  

#adding list of thread_ids to retain chats in session
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []
    
#while loading a page 
add_threads(st.session_state['thread_id'])
#******************************Sidebar UI****************************
st.sidebar.title("Your ChatBot")
#add button
if st.sidebar.button('New Chat'):
    reset_chat()
#adding header
st.sidebar.header("My Conversations")

#display list of chat threadid - to get the recent top on first
for thread_id in st.session_state['chat_threads'][::-1]:
    #making threadids as buttons to load converstaions
    if st.sidebar.button(str(thread_id)):
        #storing threadid in session
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        #we have a format to store in the message history with role - so manual code
        temp_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role ='user'
            else:
                role = 'assistant'
            temp_messages.append({'role':role,'content':message.content})
        #updating the messagehistory for that session
        st.session_state['message_history'] = temp_messages
        
#*****************UI to load conversations*************************
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
    
#userinput
user_input = st.chat_input('Text Here..')

if user_input:
    #first adding the user message to message history
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    #CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    #adding metadata and thread id for the better observability in langssmith for different threads different traces visually 
    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata":{
            "thread_id": st.session_state["thread_id"]
        },
        "run_name":"chat-turn"
        }
    # Assistant streaming block
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config={
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata":{
            "thread_id": st.session_state["thread_id"]
        },
        "run_name":"chat-turn"
        },
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    
