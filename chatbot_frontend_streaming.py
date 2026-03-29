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
        

    
    with slt.chat_message("assistant"):
        ai_message=slt.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages":[HumanMessage(content=user_input)]},
                config={"configurable":{"thread_id":"thread-1"}},
                stream_mode="messages"
            )
        )
    slt.session_state['message_history'].append({"role":"assistant","content":ai_message})
    