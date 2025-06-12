"""
Simple task management system for the AI agent
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict

@dataclass
class Task:
    """
    Data class to represent a task with type hints and default values.
    Using dataclass for clean representation and easy serialization.
    """
    id: int
    title: str
    priority: str
    completed: bool = False
    created_at: str = datetime.now().isoformat()

class TaskManager:
    """
    A task management system that persists tasks in a JSON file.
    Provides methods for CRUD operations and task statistics.
    """
    
    def __init__(self, tasks_file: str = "tasks.json") -> None:
        """
        Initialize the TaskManager with a specified JSON file.
        
        Args:
            tasks_file (str): Path to the JSON file storing tasks
        """
        self.tasks_file = tasks_file
        self.tasks = self._load_tasks()  # Store tasks in a dictionary with ID as key

    def _load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file"""
        try:
# Try to open and read the existing tasks file
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
# If file doesn't exist yet, start with empty list
            return []
    
    def _save_tasks(self) -> None:
        """
        Private method to save tasks to JSON file.
        Converts Task objects to dictionaries before saving.
        """
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, title: str, priority: str = "medium") -> str:
        """Add a new task"""
# Create a new task dictionary with all required fields
        task = {
            "id": len(self.tasks) + 1,# Simple ID generation
            "title": title,# Task description
            "priority": priority.lower(),# Normalize priority
            "completed": False,# New tasks start incomplete
            "created_at": datetime.now().isoformat()# Timestamp
        }
# Add to our tasks list and save to file
        self.tasks.append(task)
        self._save_tasks()
        return f"Task '{title}' added with {priority} priority"
    
    
    def list_tasks(self) -> str:
        """
        Return a formatted string of active tasks with emojis.
        
        Returns:
            str: Formatted string of tasks
        """
        if not self.tasks:
            return "📝 No tasks found!"
        
        # Sort tasks by priority and completion status
        sorted_tasks = sorted(
            self.tasks,
            key=lambda x: (x["completed"], x["priority"])
        )
        
        # Format each task with appropriate emojis
        task_lines = []
        for task in sorted_tasks:
            status = "✅" if task["completed"] else "⏳"
            priority_emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task["priority"].lower(), "⚪")
            
            task_lines.append(
                f"{status} {priority_emoji} Task {task['id']}: {task['title']}"
            )
        
        return "\n".join(task_lines)
    
    def complete_task(self, task_id: int) -> str:
        """
        Mark a task as completed.
        
        Args:
            task_id (int): ID of the task to complete
            
        Returns:
            str: Success or failure message
        """
        # Find task with matching ID
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                self._save_tasks()
                return f"Task '{task['title']}' marked as completed! 🎉"
        
        return f"Task with ID {task_id} not found! ❌"
    
    def get_stats(self) -> str:
        """
        Calculate and return productivity statistics with encouraging messages.
        
        Returns:
            str: Formatted statistics and encouragement
        """
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task["completed"])
        
        if total_tasks == 0:
            return "📊 No tasks yet! Time to get started! 🚀"
        
        completion_rate = (completed_tasks / total_tasks) * 100
        
        # Generate encouraging message based on completion rate
        if completion_rate == 100:
            message = "🎉 Perfect score! You're on fire! 🔥"
        elif completion_rate >= 75:
            message = "🌟 Great progress! Keep up the momentum! 💪"
        elif completion_rate >= 50:
            message = "👍 Halfway there! You're doing great! 🌈"
        else:
            message = "🌱 Every journey starts with a single step! Keep going! 💫"
        
        return f"""
📊 Task Statistics:
------------------
Total Tasks: {total_tasks}
Completed: {completed_tasks}
Completion Rate: {completion_rate:.1f}%

{message}
"""