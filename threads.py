import streamlit as st
import io
import json
from PIL import Image
from config import Config
from functions import Functions
from sqlalchemy.sql import text


class Threads():
     
    def get_db_session(self):
        session = Config.get_db_session()
        session.execute(text("CREATE TABLE IF NOT EXISTS threads (thread_id TEXT PRIMARY KEY, name TEXT, origin DATETIME)"))
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

    def get_current_threads(self):
        threads = {}
        with self.get_db_session() as session:
            results = session.execute(text("SELECT thread_id, name FROM threads order by origin")).fetchall()
            for thread_id, name in results:
                if name == None or name == "":
                    name = self.create_thread_name(thread_id)
                threads[thread_id] = name
        return threads
    
    def get_current_thread_id(self):
        thread_id = None
        if 'thread' not in st.session_state:
            thread = Config.get_openai_client().beta.threads.create()
            with self.get_db_session() as session:
                session.execute(text(f"INSERT INTO threads (thread_id, origin) VALUES ('{thread.id}', CURRENT_TIMESTAMP)"))
                session.commit()
            st.session_state['thread'] = thread.id
        thread_id = st.session_state['thread']
        return thread_id
    
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
    
    def create_thread(self):
        thread = Config.get_openai_client().beta.threads.create()
        with self.get_db_session() as session:
            session.execute(text(f"INSERT INTO threads (thread_id, origin) VALUES ('{thread.id}', CURRENT_TIMESTAMP)"))
            session.commit()
        st.session_state['thread'] = thread.id
        return thread.id
    
    def delete_thread(self, thread_id):
        Config.get_openai_client().beta.threads.delete(thread_id=thread_id)
        with self.get_db_session() as session:
            session.execute(text(f"DELETE FROM threads WHERE thread_id = '{thread_id}'"))
            session.commit()
        st.session_state['thread'] = None


if __name__ == "__main__":
    threads = Threads()

    with threads.get_db_session() as session:
        results = session.execute(text("SELECT thread_id, name FROM threads order by origin")).fetchall()
        for thread_id, name in results:
            threads.delete_thread(thread_id)
            print(f"Deleted thread {thread_id}")

