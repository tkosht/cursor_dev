#!/usr/bin/env python
"""
Quick test script for A2A MVP implementation.
"""
import sys
sys.path.append('/home/devuser/workspace')

from app.a2a_mvp.agents.task_agent import TaskAgent
from app.a2a_mvp.storage.memory import InMemoryStorage
from app.a2a_mvp.core.types import TaskRequest
import json


def main():
    """Test the A2A MVP implementation."""
    print("=== A2A MVP Test ===\n")
    
    # Initialize agent
    storage = InMemoryStorage()
    agent = TaskAgent(storage)
    
    # Get agent card
    print("1. Agent Card:")
    card = agent.get_agent_card()
    print(f"   Name: {card.name}")
    print(f"   Version: {card.version}")
    print(f"   Skills: {len(card.skills)} available")
    print()
    
    # Create tasks
    print("2. Creating tasks...")
    tasks_to_create = [
        {"title": "Buy groceries", "description": "Milk, bread, eggs"},
        {"title": "Complete A2A implementation"},
        {"title": "Write documentation", "description": "Update README"}
    ]
    
    created_tasks = []
    for task_data in tasks_to_create:
        request = TaskRequest(action="create", data=task_data)
        response = agent.process_request(request)
        if response.success:
            created_tasks.append(response.data)
            print(f"   ✓ Created: {response.data['title']}")
        else:
            print(f"   ✗ Failed: {response.error}")
    print()
    
    # List tasks
    print("3. Listing all tasks...")
    request = TaskRequest(action="list")
    response = agent.process_request(request)
    if response.success:
        for task in response.data['tasks']:
            status = "✓" if task['completed'] else "○"
            print(f"   {status} [{task['id'][:8]}] {task['title']}")
    print()
    
    # Toggle completion
    if created_tasks:
        print("4. Toggling first task completion...")
        first_task_id = created_tasks[0]['id']
        request = TaskRequest(action="toggle", task_id=first_task_id)
        response = agent.process_request(request)
        if response.success:
            print(f"   ✓ Task marked as {'completed' if response.data['completed'] else 'pending'}")
    print()
    
    # Test A2A message handling
    print("5. Testing A2A message handling...")
    a2a_message = {
        "action": "create",
        "data": {"title": "A2A Protocol Task"}
    }
    result = agent.handle_a2a_message(a2a_message)
    if result['success']:
        print(f"   ✓ A2A message handled successfully")
        print(f"   Created task: {result['data']['title']}")
    else:
        print(f"   ✗ A2A message failed: {result['error']}")
    print()
    
    # Final task count
    request = TaskRequest(action="list")
    response = agent.process_request(request)
    if response.success:
        print(f"Total tasks: {response.data['count']}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()