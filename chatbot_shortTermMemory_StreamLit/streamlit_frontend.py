import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

#we need config and thread
CONFIG = {'configurable':{'thread_id':'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] =[]
#chat history
#message_history = [] #as this will reset entire message history to empty list everytime the conversation is lost
# hence in streamlit we have  session state component which is a dict and even if it is rerun the conversation history is not lost and it will refresh only if  you manually refresh the session on chrome
#st.session_state ->dict->
#messgae history stores dict of messages with role as:
#{'role':'user,'content':'Hi'}
#{'role':'assistant','content':'Hello'}

#loading entire conversation history
#for message in message_history:
for  message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type Here..')

if user_input:
    #adding message to message history
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    #invoking chatbot to get the llm response
    response = chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config = CONFIG)
    ai_message = response['messages'][-1].content
    
    #adding message to message history
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)