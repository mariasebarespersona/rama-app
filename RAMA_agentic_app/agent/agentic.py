import openai
from agent.tools.database_tool import DatabaseTool
from agent.tools.document_tool import DocumentTool
import os
import time

user_threads = {}

class AssistantManager:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.db_tool = DatabaseTool()
        self.doc_tool = DocumentTool()

        self.assistant = openai.beta.assistants.create(
            name="RAMA Real Estate Assistant",
            instructions="You are an assistant that helps manage real estate investments. You can provide document summaries, access property data, and analyze payment stages. And send emails with documents if requested by the user." \
            "A user can also ask you to delete documents directly in the chat. "\
            "Always reply in Spanish",

            model="gpt-4o",
            tools=[{"type": "function", "function": {
                "name": "get_property_stats",
                "description": "Get summary statistics of properties by status",
                "parameters": {}
            }},
            {"type": "function", "function": {
                "name": "list_documents",
                "description": "Get a list of all documents per property",
                "parameters": {}
            }},
            {"type": "function", "function": {
                "name": "email_document",
                "description": "Send a document by email if user provides the property address, document name and email address to send it to.",
                "parameters": {
                    "type":"object",
                    "properties":{
                        "property_address":{"type":"string"},
                        "document_name":{"type":"string", "description":"The name of the document to send(e.g., builder_payment.pdf or builder_payment)"},
                        "email":{"type":"string", "format":"email"}
                    },
                    "required":["property_address","document_name","email"]
                }
            }},
            {"type": "function", "function": {
                "name": "delete_documents_chat",
                "description": "Delete documents when a person asks you to do so via the chat.",
                "parameters": {
                    "type":"object",
                    "properties":{
                        "address":{"type":"string"},
                        "category":{"type":"string"},
                        "document_type":{"type":"string"}
                    },
                    "required":["address", "category", "document_type"]
                }
            }}
            ]
        )

    def get_or_create_thread(self, user_id: str):
        if user_id in user_threads:
            return user_threads[user_id]
        thread = openai.beta.threads.create()
        user_threads[user_id] = thread.id
        return thread.id

    def handle_message(self, user_message: str, user_id: str = "default"):

        thread_id = self.get_or_create_thread(user_id)
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id
        )
        deletion_args = None  
        while True:
            # run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            # if run.status == "requires_action":
            #     tool_outputs = []
            #     for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            #         fn_name = tool_call.function.name
            #         if fn_name == "list_documents":
            #             result = self.doc_tool.list_documents()
            #         elif fn_name == "get_property_stats":
            #             result = str(self.db_tool.get_property_stats())
            #         elif fn_name == "delete_documents_chat":
            #             args=eval(tool_call.function.arguments)
            #             result = self.doc_tool.delete_documents_chat(
            #                 address=args["address"],
            #                 category=args["category"],
            #                 document_type=args["document_type"],
            #             )
                        
            #         elif fn_name=="email_document":
            #             args=eval(tool_call.function.arguments)
            #             result=self.doc_tool.email_document(
            #                 property_address=args["property_address"],
            #                 document_name=args['document_name'],
            #                 email=args["email"]
            #             )
                    
            #         else:
            #             result = "Unknown tool"

            #         tool_outputs.append({
            #             "tool_call_id": tool_call.id,
            #             "output": str(result)
            #         })

            #     run = openai.beta.threads.runs.submit_tool_outputs(
            #         thread_id=thread_id,
            #         run_id=run.id,
            #         tool_outputs=tool_outputs
            #     )

            # elif run.status == "completed":
            #     break

            # elif run.status in ("failed", "cancelled", "expired"):
            #     return "❌ Assistant run failed."
            


            # time.sleep(1)
            run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            if run.status == "requires_action":
                tool_outputs = []

                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    fn_name = tool_call.function.name
                    args = eval(tool_call.function.arguments)

                    if fn_name == "list_documents":
                        result = self.doc_tool.list_documents()
                    elif fn_name == "get_property_stats":
                        result = str(self.db_tool.get_property_stats())
                    elif fn_name == "delete_documents_chat":
                        result = self.doc_tool.delete_documents_chat(
                            address=args["address"],
                            category=args["category"],
                            document_type=args["document_type"],
                        )
                        deletion_args = args 
                    elif fn_name == "email_document":
                        result = self.doc_tool.email_document(
                            property_address=args["property_address"],
                            document_name=args["document_name"],
                            email=args["email"]
                        )
                    else:
                        result = "Unknown tool"

                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": str(result)  
                    })

                run = openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run.status == "completed":
                break

            elif run.status in ("failed", "cancelled", "expired"):
                return "❌ Assistant run failed."

            time.sleep(1)

    
        if deletion_args:
            followup_text = (
                f"The document(s) related to '{deletion_args['document_type']}' at "
                f"{deletion_args['address']} in the '{deletion_args['category']}' category "
                f"were deleted and are no longer available."
            )
            openai.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=followup_text
            )

          
            followup_run = openai.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant.id
            )

     
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=followup_run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status in ("failed", "cancelled", "expired"):
                    return "❌ Follow-up run failed."
                time.sleep(1)
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        return messages.data[0].content[0].text.value