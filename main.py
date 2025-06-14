"""
AI Task Manager Agent
Demonstrates OpenAI SDK usage with tool calling
"""
import os# For environment variables
import json# For parsing function arguments
from dotenv import load_dotenv# For loading .env file
from openai import OpenAI# The OpenAI SDK
from taskmanager import TaskManager# Our business logic# Load environment variables from .env file
load_dotenv()

class AITaskAgent:
    def __init__(self):
        # Initialize OpenAI client with API key from environment
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Create task manager instance for handling task operations
        self.task_manager = TaskManager()

        # Define available tools for the AI to use
        # Each tool represents a capability the AI can use to help users
        #(USE PRPOMPT TO BUILD THIS)
        self.tools = [
            {
                "type": "function",
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
                    "required": ["title", "priority"],
                    "additionalProperties": False
                },
                "strict": True
            },
            {
                "type": "function",
                "name": "list_tasks",
                "description": "Get a formatted list of all tasks with their status and priority",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False
                },
                "strict": True
            },
            {
                "type": "function",
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
                    "required": ["task_id"],
                    "additionalProperties": False
                },
                "strict": True
            },
            {
                "type": "function",
                "name": "get_stats",
                "description": "Get productivity statistics and encouraging messages about task completion",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False
                },
                "strict": True
            }
        ]

    def execute_tool(self, tool_call):
        """
        Execute the requested tool and return its result.
        This is where we map tool calls to actual TaskManager methods.
        """
        # Extract tool name and arguments
        name = tool_call.name
        args = json.loads(tool_call.arguments)
        
        # Map tool calls to TaskManager methods
        if name == "add_task":
            return self.task_manager.add_task(
                args["title"],
                args.get("priority", "medium")
            )
        elif name == "list_tasks":
            return self.task_manager.list_tasks()
        elif name == "complete_task":
            return self.task_manager.complete_task(args["task_id"])
        elif name == "get_stats":
            return self.task_manager.get_stats()
        else:
            return f"Unknown tool: {name}"

    def chat(self, user_message: str) -> str:
        """
        Process user message and return AI response using the new tool calling structure.
        This method demonstrates the complete flow of:
        1. Initial request processing
        2. Tool execution
        3. Result incorporation
        4. Final response generation
        """
        try:
            # Step 1: Initial request to the model
            # The model will decide if it needs to use any tools
            response = self.client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "system",
                        "content": """You are a helpful AI assistant that manages tasks for users. 
                        You can add tasks, list tasks, mark tasks as completed, and provide productivity insights.
                        Be friendly, encouraging, and help users stay organized and productive.
                        Always use the available tools to interact with the task management system."""
                    },
                    {"role": "user", "content": user_message}
                ],
                tools=self.tools,
                tool_choice="auto"
            )
            
            # Step 2: Check if model wants to use any tools
            if response.output and response.output[0].type == "function_call":
                # Get the tool call details
                tool_call = response.output[0]
                
                # Step 3: Execute the requested tool
                tool_result = self.execute_tool(tool_call)
                
                # Step 4: Supply the result back to the model
                # We append both the tool call and its result to the conversation
                input_messages = [
                    {
                        "role": "system",
                        "content": """You are a helpful AI assistant that manages tasks for users. 
                        Be friendly, encouraging, and help users stay organized and productive."""
                    },
                    {"role": "user", "content": user_message},
                    tool_call,  # The model's tool call
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": str(tool_result)
                    }
                ]
                
                # Step 5: Get final response incorporating the tool result
                final_response = self.client.responses.create(
                    model="gpt-4.1",
                    input=input_messages,
                    tools=self.tools
                )
                
                return final_response.output_text
            else:
                # If no tools were needed, return the direct response
                return response.output_text
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

def main():
    """
    Main entry point of the application.
    Sets up the interactive command-line interface for the task manager.
    """
    print("🤖 AI Task Manager Agent")
    print("=" * 30)
    print("I can help you manage your tasks! Try saying:")
    print("- 'Add a task to buy groceries'")
    print("- 'Show me my tasks'")
    print("- 'Complete task 1'")
    print("- 'Show my productivity stats'")
    print("- Type 'quit' to exit")
    print()
    
    # Create the AI agent instance
    agent = AITaskAgent()
    
    # Main interaction loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for exit command
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye! Stay productive!")
            break
        
        # Skip empty input
        if not user_input:
            continue
        
        # Get and display AI response
        print("🤖 Agent:", agent.chat(user_input))
        print()

if __name__ == "__main__":
    main()
