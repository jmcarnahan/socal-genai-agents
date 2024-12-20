import streamlit as st
import io
import json
from PIL import Image
from config import Config
from functions import Functions
from sqlalchemy.sql import text


class Threads:
     
    user_id: str = None

    def __init__(self, user_id):
        self.user_id = user_id

    def get_db_session(self):
        session = Config.get_db_session()
        session.execute(text("CREATE TABLE IF NOT EXISTS threads (thread_id TEXT PRIMARY KEY, name TEXT, user_id TEXT, origin DATETIME)"))
        session.commit()
        return session

    def create_thread_name(self, thread_id):
        thread_name = "New Thread"
        messages = Config.get_openai_client().beta.threads.messages.list(thread_id=thread_id, limit=1, order="asc")
        if len(messages.data) > 0:
            thread_name = messages.data[0].content[0].text.value
            with self.get_db_session() as session:
                session.execute(text(f"UPDATE threads SET name = '{thread_name}' WHERE thread_id = '{thread_id}'"))
                session.commit()
        return thread_name

    def get_current_threads(self, count=10):
        threads = []
        with self.get_db_session() as session:
            results = session.execute(text(f"SELECT thread_id, name, origin FROM threads where user_id = '{self.user_id}' order by origin DESC LIMIT {count}")).fetchall()
            for thread_id, name, origin in results:
                if name == None or name == "":
                    name = self.create_thread_name(thread_id)
                threads.append({"thread_id": thread_id, "name": name, "origin": origin})
        return threads
        
    def create_thread(self):
        thread = Config.get_openai_client().beta.threads.create()
        with self.get_db_session() as session:
            session.execute(text(f"INSERT INTO threads (thread_id, user_id, origin) VALUES ('{thread.id}', '{self.user_id}', CURRENT_TIMESTAMP)"))
            session.commit()
        return thread.id

    def get_current_thread_id(self):
        if 'thread' not in st.session_state:
            threads = self.get_current_threads(count=1)
            if len(threads) > 0:
                st.session_state['thread'] = threads[0]['thread_id']
            else:
                st.session_state['thread'] = self.create_thread()
        return st.session_state['thread']
    
    def get_messages(self, thread_id, limit=20):
        response_msgs = []
        messages = Config.get_openai_client().beta.threads.messages.list(thread_id=thread_id, limit=limit, order="asc")
        for message in messages.data:
            part_idx = 0
            for part in message.content:
                part_idx += 1
                part_id = f"{message.id}_{part_idx}"
                if part.type == "text":
                    response_msgs.append({"id": part_id, "role": message.role, "content": part.text.value})
                elif part.type == "image_file":
                    response_content = Config.get_openai_client().files.content(part.image_file.file_id)
                    data_in_bytes = response_content.read()
                    readable_buffer = io.BytesIO(data_in_bytes)
                    image = Image.open(readable_buffer)
                    response_msgs.append({"id": part_id, "role": message.role, "content": image})
        return {message['id']: message for message in response_msgs}

    
    def delete_thread(self, thread_id):
        Config.get_openai_client().beta.threads.delete(thread_id=thread_id)
        with self.get_db_session() as session:
            session.execute(text(f"DELETE FROM threads WHERE thread_id = '{thread_id}'"))
            session.commit()
        st.session_state['thread'] = None

    def display_threads(self):

        st.markdown("## Threads")

        current_thread_id = self.get_current_thread_id()

        if st.button("Create New Thread"):
            thread_id = self.create_thread()
            st.session_state['thread'] = thread_id
            st.rerun()

        for thread in self.get_current_threads():
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if thread['thread_id'] == current_thread_id:
                    st.markdown(f"<span style='color:lightgreen'>{thread['name']}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"{thread['name']}")
            with col2:
                st.markdown(f"{thread['origin']}")
            with col3:
                button1, button2 = st.columns([1, 1])
                with button1:
                    if thread['thread_id'] == current_thread_id:
                        st.button(label=f"Select", disabled=True, key=f"Select {thread['thread_id']}")
                    else:
                        if st.button(label=f"Select", key=f"Select {thread['thread_id']}"):
                            st.session_state['thread'] = thread['thread_id']
                            st.rerun()
                with button2:
                    if thread['thread_id'] == current_thread_id:
                        st.button(label=f"Delete", disabled=True, key=f"Delete {thread['thread_id']}")
                    else:
                        if st.button(label=f"Delete", key=f"Delete {thread['thread_id']}"):
                            self.delete_thread(thread['thread_id'])
                            st.rerun()





if __name__ == "__main__":
    threads = Threads()

    with threads.get_db_session() as session:
        results = session.execute(text("SELECT thread_id, name FROM threads order by origin")).fetchall()
        for thread_id, name in results:
            threads.delete_thread(thread_id)
            print(f"Deleted thread {thread_id}")

