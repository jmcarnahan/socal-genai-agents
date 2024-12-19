import streamlit as st
import io
import json
from PIL import Image
from config import Config
from functions import Functions
from threads import Threads

class ChatPage():

    assistant_id: str = None
    title: str = None

    def __init__(self, assistant_id=None, title=None):
        self.assistant_id = assistant_id
        self.title = title
        self.openai_client = Config.get_openai_client()

    def display_content(self, content):
        if isinstance(content, str):
            st.markdown(content)
        elif isinstance(content, Image.Image):
            st.image(content)

    def get_messages(self, thread_id):
        response_msgs = []
        messages = self.openai_client.beta.threads.messages.list(
            thread_id=thread_id
        )
        for message in reversed(messages.data):
            part_idx = 0
            for part in message.content:
                part_idx += 1
                part_id = f"{message.id}_{part_idx}"
                if part.type == "text":
                    response_msgs.append({"id": part_id, "role": message.role, "content": part.text.value})
                elif part.type == "image_file":
                    response_content = self.openai_client.files.content(part.image_file.file_id)
                    data_in_bytes = response_content.read()
                    readable_buffer = io.BytesIO(data_in_bytes)
                    image = Image.open(readable_buffer)
                    response_msgs.append({"id": part_id, "role": message.role, "content": image})
        return response_msgs


    def get_response(self, prompt, thread_id):
        self.openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt,
        )

        run = self.openai_client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
        )
        
        for i in range(100):
            match run.status:
                case "completed":
                    return self.get_messages(thread_id)
                case "failed":
                    raise Exception("Run failed")
                case "expired":
                    raise Exception("Run expired")
                case "cancelled":
                    raise Exception("Run cancelled")
                case "requires_action":
                    # Loop through each tool in the required action section
                    tool_outputs = []
                    for tool in run.required_action.submit_tool_outputs.tool_calls:
                        function_to_call = getattr(Functions, tool.function.name, None)
                        if function_to_call:
                            try:
                                print(f"Calling function {tool.function}")
                                parameters = json.loads(tool.function.arguments) if hasattr(tool.function, 'arguments') else {}
                                result = function_to_call(**parameters)
                                tool_outputs.append({
                                    "tool_call_id": tool.id,
                                    "output": result
                                })
                            except Exception as e:
                                print(f"Error calling function {tool.function.name}: {e}")

                    # Submit all tool outputs at once after collecting them in a list
                    if tool_outputs:
                        try:
                            run = self.openai_client.beta.threads.runs.submit_tool_outputs_and_poll(
                                thread_id=thread_id,
                                run_id=run.id,
                                tool_outputs=tool_outputs
                            )
                            #print("Tool outputs submitted successfully.")
                        except Exception as e:
                            print("Failed to submit tool outputs:", e)
                    else:
                        print("No tool outputs to submit.")



    def display_chatbot(self):

        st.markdown(f"## {self.title}")

        thread_id = Threads().get_current_thread_id()
        messages_key = f"{thread_id}-messages"

        # Initialize chat history
        if messages_key not in st.session_state:
            st.session_state[messages_key] = Threads().get_messages(thread_id)
        
        for message in st.session_state[messages_key].values():
            with st.chat_message(message["role"]):
                self.display_content(message["content"])

        if prompt := st.chat_input("What is up?"):
            for message in self.get_response(prompt, thread_id):
                if message["id"] not in st.session_state[messages_key]:
                    st.session_state[messages_key][message["id"]] = message
                    with st.chat_message(message["role"]):
                        self.display_content(message["content"])



        
                    


