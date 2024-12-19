# import importlib
# import pkgutil

# from dotenv import load_dotenv
import streamlit as st
from config import Config
from chat_page import ChatPage
from threads import Threads



def home_page():
    st.markdown("## Welcome to the Home Page")

def create_threads_page(user_id=""):
    def threads_page():
        st.markdown("## Threads")

        current_thread_id = ''
        if 'thread' in st.session_state:
            current_thread_id = st.session_state['thread']

        if st.button("Create New Thread"):
            thread_id = Threads().create_thread()
            st.session_state['thread'] = thread_id
            st.rerun()

        current_threads = Threads().get_current_threads()
        for thread_id, name in current_threads.items():
            col1, col2 = st.columns([1, 1])
            with col1:
                if thread_id == current_thread_id:
                    st.markdown(f"<span style='color:lightgreen'>{name}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"{name}")
            with col2:
                button1, button2 = st.columns([1, 1])
                with button1:
                    if thread_id == current_thread_id:
                        st.button(label=f"Select", disabled=True, key=f"Select {thread_id}")
                    else:
                        if st.button(label=f"Select", key=f"Select {thread_id}"):
                            st.session_state['thread'] = thread_id
                            st.rerun()
                with button2:
                    if thread_id == current_thread_id:
                        st.button(label=f"Delete", disabled=True, key=f"Delect {thread_id}")
                    else:
                        if st.button(label=f"Delete", key=f"Delect {thread_id}"):
                            Threads().delete_thread(thread_id)
                            st.rerun()

    return threads_page


def create_chat_page(assistant_id, title):
    def dynamic_function():
        return ChatPage(assistant_id=assistant_id, title=title).display_chatbot()
    dynamic_function.__name__ = f"chat_bot_{assistant_id}"
    return dynamic_function


def main_page():

    openai_client = Config.get_openai_client()
    assistants = openai_client.beta.assistants.list(order="desc",limit="20")

    pages = []
    pages.append(st.Page(home_page, title="Home Page"))
    pages.append(st.Page(create_threads_page(user_id=""), title="Threads"))

    for asst in assistants.data:
        pages.append(st.Page(create_chat_page(assistant_id=asst.id, title=asst.name), title=asst.name))

    pg = st.navigation(pages)
    st.set_page_config(page_title="Home", page_icon="🧊", layout="wide")
    pg.run()



if __name__ == "__main__":
    # main()
    main_page()