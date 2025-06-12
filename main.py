"""
AI Task Manager Agent
Demonstrates OpenAI SDK usage with function calling
"""
import os# For environment variables
import json# For parsing function arguments
from dotenv import load_dotenv# For loading .env file
from openai import OpenAI# The OpenAI SDK
from taskmanager import TaskManager# Our business logic# Load environment variables from .env file
load_dotenv()

class AITaskAgent:
    def __init__(self):
# Create OpenAI client with API key from environment
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Create our task manager instance
        self.task_manager = TaskManager()

# Define available functions for the AI to call# This is the "menu" of actions the AI can perform
        self.functions = [
            {
                "name": "add_task",
                "description": "Add a new task to the task manager",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title or description of the task"
                        },
                        "priority": {
                            "type": "string",
                            "description": "The priority level of the task (high, medium, or low)",
                            "enum": ["high", "medium", "low"]
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "list_tasks",
                "description": "Get a formatted list of all tasks with their status and priority",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "complete_task",
                "description": "Mark a specific task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to mark as completed"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "get_stats",
                "description": "Get productivity statistics and encouraging messages about task completion",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    def call_function(self, function_name: str, arguments: dict) -> str:
        """Execute the requested function"""
        if function_name == "add_task":
            return self.task_manager.add_task(
                arguments["title"], 
                arguments.get("priority", "medium")
            )
        elif function_name == "list_tasks":
            return self.task_manager.list_tasks()
        elif function_name == "complete_task":
            return self.task_manager.complete_task(arguments["task_id"])
        elif function_name == "get_stats":
            return self.task_manager.get_stats()
        else:
            return f"Unknown function: {function_name}"
    
    def chat(self, user_message: str) -> str:
        """Process user message and return AI response"""
        try:
            # Create chat completion with function calling
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful AI assistant that manages tasks for users. 
                        You can add tasks, list tasks, mark tasks as completed, and provide productivity insights.
                        Be friendly, encouraging, and help users stay organized and productive.
                        Always use the available functions to interact with the task management system."""
                    },
                    {"role": "user", "content": user_message}
                ],
                functions=self.functions,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            # Check if AI wants to call a function
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                
                # Execute the function
                function_result = self.call_function(function_name, function_args)
                
                # Get AI's response after function execution
                second_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        # 1. System Message
                        {
                            "role": "system",
                            "content": """You are a helpful AI assistant that manages tasks for users. 
                            Be friendly, encouraging, and help users stay organized and productive."""
                        },
                         # 2. Original User Message
                        {"role": "user", "content": user_message},
                        # 3. Assistant's Function Call
                        {
                            "role": "assistant",
                            "content": None,
                            "function_call": {
                                "name": function_name,
                                "arguments": json.dumps(function_args)
                            }
                        },
                         # 4. Function Result
                        {
                            "role": "function",
                            "name": function_name,
                            "content": function_result
                        }
                    ]
                )
                
                return second_response.choices[0].message.content
            else:
                return message.content
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

def main():
    print("🤖 AI Task Manager Agent")
    print("=" * 30)
    print("I can help you manage your tasks! Try saying:")
    print("- 'Add a task to buy groceries'")
    print("- 'Show me my tasks'")
    print("- 'Complete task 1'")
    print("- 'Show my productivity stats'")
    print("- Type 'quit' to exit")
    print()
    
    agent = AITaskAgent()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye! Stay productive!")
            break
        
        if not user_input:
            continue
        
        print("🤖 Agent:", agent.chat(user_input))
        print()

if __name__ == "__main__":
    main()
