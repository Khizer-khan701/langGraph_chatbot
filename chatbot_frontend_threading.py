import streamlit as slt
from chatbot_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ****************************** Utilities Functions **************************

def generate_thread_id():
    # UUID ko string mein convert karna zaroori hai
    return str(uuid.uuid4())

def reset_chat():
    new_id = generate_thread_id()
    slt.session_state["thread_id"] = new_id
    add_thread(new_id)
    # Screen clear karne ke liye history khali karein
    slt.session_state["message_history"] = []
    # UI refresh karne ke liye rerun lazmi hai
    slt.rerun()

def add_thread(thread_id):
    if "chat_thread" not in slt.session_state:
        slt.session_state["chat_thread"] = []
    
    # Check karne se pehle string mein convert kar lein taake duplicate na hon
    str_id = str(thread_id)
    if str_id not in slt.session_state["chat_thread"]:
        slt.session_state["chat_thread"].append(str_id)

def load_conversation(thread_id):
    # Safe check: Agar state na mile ya messages na hon to khali list return karein
    state = chatbot.get_state(config={"configurable": {'thread_id': str(thread_id)}})
    return state.values.get('messages', [])

# ****************************** Session Setup *********************************

if 'message_history' not in slt.session_state:
    slt.session_state['message_history'] = []

if "thread_id" not in slt.session_state:
    slt.session_state["thread_id"] = generate_thread_id()

if "chat_thread" not in slt.session_state:
    slt.session_state["chat_thread"] = []
    # Thread ID ko list mein add karte waqt hamesha add_thread function use karein
    add_thread(slt.session_state["thread_id"])

# ******************************* Sidebar UI ***********************************

slt.sidebar.title("LangGraph Chatbot")

if slt.sidebar.button("New Chat"):
    reset_chat()

slt.sidebar.header("Chat History")

# Threads ko reverse order mein dikhayein
for t_id in slt.session_state["chat_thread"][::-1]:
    # ERROR FIX: t_id ko string mein convert kiya taake [:8] slicing kaam kare
    str_t_id = str(t_id)
    
    if slt.sidebar.button(f"Chat: {str_t_id[:8]}...", key=f"btn_{str_t_id}"):
        slt.session_state["thread_id"] = str_t_id
        messages = load_conversation(str_t_id)
        
        # UI ke liye messages format karein
        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({"role": role, "content": msg.content})
        
        slt.session_state['message_history'] = temp_messages
        slt.rerun()

slt.sidebar.divider()
slt.sidebar.write(f"**Current Thread:**\n{slt.session_state['thread_id']}")

# ************************************ Main UI *********************************

user_input = slt.chat_input("Type Here")

# Purani messages screen par dikhayein
for message in slt.session_state['message_history']:
    with slt.chat_message(message['role']):
        slt.markdown(message['content'])

if user_input:
    # User message add karein
    slt.session_state['message_history'].append({"role": "user", "content": user_input})
    with slt.chat_message("user"):
        slt.markdown(user_input)
        
    CONFIG = {'configurable': {"thread_id": str(slt.session_state["thread_id"])}}
    
    # Assistant response (Streaming)
    with slt.chat_message("assistant"):
        ai_message = slt.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )
    
    # AI message history mein save karein
    slt.session_state['message_history'].append({"role": "assistant", "content": ai_message})