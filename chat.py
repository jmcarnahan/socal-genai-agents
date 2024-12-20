import streamlit as st
import io
import json
from PIL import Image
from config import Config
from functions import Functions
from threads import Threads
from agent import Agent

class Chat:

    agent: Agent = None
    title: str = None
    threads: Threads = None

    def __init__(self, assistant_id, title, threads):
        if 'functions' not in st.session_state:
            st.session_state['functions'] = Functions()
        self.agent = Agent(assistant_id=assistant_id, functions=st.session_state['functions'])
        self.title = title
        self.threads = threads

    def display_content(self, content):
        if isinstance(content, str):
            st.markdown(content)
        elif isinstance(content, Image.Image):
            st.image(content)

    def display_chatbot(self):

        st.markdown(f"## {self.title}")

        thread_id = self.threads.get_current_thread_id()
        messages_key = f"{self.threads.user_id}-{thread_id}-messages"

        # Initialize chat history
        if messages_key not in st.session_state:
            st.session_state[messages_key] = self.threads.get_messages(thread_id)
        
        for message in st.session_state[messages_key].values():
            with st.chat_message(message["role"]):
                self.display_content(message["content"])

        if prompt := st.chat_input("What is up?"):
            for message in self.agent.get_response(prompt, thread_id):
                if message["id"] not in st.session_state[messages_key]:
                    st.session_state[messages_key][message["id"]] = message
                    with st.chat_message(message["role"]):
                        self.display_content(message["content"])



        
                    


