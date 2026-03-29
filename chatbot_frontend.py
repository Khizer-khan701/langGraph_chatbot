import streamlit as slt
from chatbot_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG={"configurable":{"thread_id":"thread-1"}}

if 'message_history' not in slt.session_state:
    slt.session_state['message_history']=[]


user_input=slt.chat_input("Type Here")


for message in slt.session_state['message_history']:
    with slt.chat_message(message['role']):
        slt.text(message['content'])

if user_input:
    
    slt.session_state['message_history'].append({"role":"user","content":user_input})
    with slt.chat_message("user"):
        slt.text(user_input)
        
    response=chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=CONFIG)
    ai_message=response['messages'][-1].content
    
    slt.session_state['message_history'].append({"role":"assistant","content":ai_message})
    with slt.chat_message("assistant"):
        slt.text(ai_message)