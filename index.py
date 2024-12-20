# import importlib
# import pkgutil

# from dotenv import load_dotenv
import streamlit as st
from config import Config
from chat import Chat
from threads import Threads
import logging
import os
from streamlit_google_auth import Authenticate
from dotenv import load_dotenv

load_dotenv()


def get_authenticator():
    if 'authenticator' not in st.session_state:
        st.session_state['authenticator'] = Authenticate(
            secret_credentials_path = os.getenv('GOOGLE_AUTH_CREDS_PATH'),
            cookie_name=os.getenv('GOOGLE_AUTH_COOKIE_NAME'),
            cookie_key=os.getenv('GOOGLE_AUTH_COOKIE_KEY'),
            redirect_uri=os.getenv('GOOGLE_AUTH_REDIRECT_URI'),
        )
    return st.session_state['authenticator']

def create_home_page(name=""):
    def home_page():
        st.markdown("## Home Page")
        st.markdown(f"### Welcome {name}")
        if name != "":
            if st.button('Log out'):
                get_authenticator().logout()
    return home_page

def create_threads_page(threads):
    def threads_page():
        return threads.display_threads()
    return threads_page


def create_chat_page(assistant_id, title, threads):
    def dynamic_function():
        return Chat(assistant_id=assistant_id, title=title, threads=threads).display_chatbot()
    dynamic_function.__name__ = f"chat_{assistant_id}"
    return dynamic_function


def create_login_page():
    def login_page():
        authenticator = get_authenticator()
        authenticator.check_authentification()
        authenticator.login()
    return login_page


def main_pages(name, email):
    pages = {}
    openai_client = Config.get_openai_client()
    assistants = openai_client.beta.assistants.list(order="desc",limit="20")

    user_threads = Threads(user_id=email)

    account = []
    account.append(st.Page(create_home_page(name=name), title="Home Page"))
    account.append(st.Page(create_threads_page(user_threads), title="Threads"))
    pages["Account"] = account

    agents = []
    for asst in assistants.data:
        agents.append(st.Page(create_chat_page(assistant_id=asst.id, title=asst.name, threads=user_threads), title=asst.name))
    pages["Agents"] = agents

    return pages

def main (name, email):
    pages = main_pages(name, email)
    pg = st.navigation(pages)
    st.set_page_config(page_title="Home", layout="wide")
    pg.run()

def login_main():
    pages = {}
    if 'connected' in st.session_state and st.session_state['connected']:
        name  = st.session_state['user_info'].get('name')
        email = st.session_state['user_info'].get('email')
        pages = main_pages(name, email)
    else:
        pages = {'Login': [st.Page(create_login_page(), title="Login")]}
    pg = st.navigation(pages)
    st.set_page_config(page_title="Home", layout="wide")
    pg.run()



if __name__ == "__main__":
    if os.getenv('GOOGLE_AUTH_ENABLED', "False").lower() == "true":
        login_main()
    else:
        main("", "Guest")



