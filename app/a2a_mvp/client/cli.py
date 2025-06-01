"""
CLI client for A2A Task Manager.
"""
import click
import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime


class TaskClient:
    """Client for interacting with A2A Task Manager."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        response = requests.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.json()
    
    def create_task(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new task."""
        data = {"title": title}
        if description:
            data["description"] = description
        
        response = requests.post(
            f"{self.base_url}/task",
            json={"action": "create", "data": data}
        )
        response.raise_for_status()
        return response.json()
    
    def list_tasks(self) -> Dict[str, Any]:
        """List all tasks."""
        response = requests.post(
            f"{self.base_url}/task",
            json={"action": "list"}
        )
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task."""
        response = requests.post(
            f"{self.base_url}/task",
            json={"action": "get", "task_id": task_id}
        )
        response.raise_for_status()
        return response.json()
    
    def update_task(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """Update a task."""
        response = requests.post(
            f"{self.base_url}/task",
            json={"action": "update", "task_id": task_id, "data": kwargs}
        )
        response.raise_for_status()
        return response.json()
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task."""
        response = requests.post(
            f"{self.base_url}/task",
            json={"action": "delete", "task_id": task_id}
        )
        response.raise_for_status()
        return response.json()
    
    def toggle_task(self, task_id: str) -> Dict[str, Any]:
        """Toggle task completion."""
        response = requests.post(
            f"{self.base_url}/task",
            json={"action": "toggle", "task_id": task_id}
        )
        response.raise_for_status()
        return response.json()


@click.group()
@click.option('--url', default='http://localhost:8000', help='A2A server URL')
@click.pass_context
def cli(ctx, url):
    """A2A Task Manager CLI."""
    ctx.ensure_object(dict)
    ctx.obj['client'] = TaskClient(url)


@cli.command()
@click.pass_context
def info(ctx):
    """Get agent information."""
    client = ctx.obj['client']
    try:
        info = client.get_agent_info()
        click.echo(f"Agent: {info['name']} v{info['version']}")
        click.echo(f"Description: {info['description']}")
        click.echo(f"\nCapabilities:")
        click.echo(f"  Streaming: {info['capabilities']['streaming']}")
        click.echo(f"  Push Notifications: {info['capabilities']['push_notifications']}")
        click.echo(f"\nSkills:")
        for skill in info['skills']:
            click.echo(f"  - {skill['name']} ({skill['id']})")
            click.echo(f"    {skill['description']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.pass_context
def create(ctx, title, description):
    """Create a new task."""
    client = ctx.obj['client']
    try:
        result = client.create_task(title, description)
        task = result['data']
        click.echo(f"Created task: {task['id']}")
        click.echo(f"Title: {task['title']}")
        if task.get('description'):
            click.echo(f"Description: {task['description']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.pass_context
def list(ctx):
    """List all tasks."""
    client = ctx.obj['client']
    try:
        result = client.list_tasks()
        tasks = result['data']['tasks']
        count = result['data']['count']
        
        if count == 0:
            click.echo("No tasks found.")
        else:
            click.echo(f"Tasks ({count}):")
            for task in tasks:
                status = "✓" if task['completed'] else "○"
                click.echo(f"{status} [{task['id'][:8]}] {task['title']}")
                if task.get('description'):
                    click.echo(f"  {task['description']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('task_id')
@click.pass_context
def get(ctx, task_id):
    """Get a specific task."""
    client = ctx.obj['client']
    try:
        result = client.get_task(task_id)
        task = result['data']
        
        click.echo(f"Task: {task['id']}")
        click.echo(f"Title: {task['title']}")
        if task.get('description'):
            click.echo(f"Description: {task['description']}")
        click.echo(f"Status: {'Completed' if task['completed'] else 'Pending'}")
        click.echo(f"Created: {task['created_at']}")
        if task.get('updated_at'):
            click.echo(f"Updated: {task['updated_at']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('task_id')
@click.option('--title', '-t', help='New title')
@click.option('--description', '-d', help='New description')
@click.option('--complete/--incomplete', default=None, help='Set completion status')
@click.pass_context
def update(ctx, task_id, title, description, complete):
    """Update a task."""
    client = ctx.obj['client']
    try:
        updates = {}
        if title:
            updates['title'] = title
        if description:
            updates['description'] = description
        if complete is not None:
            updates['completed'] = complete
        
        if not updates:
            click.echo("No updates specified.", err=True)
            return
        
        result = client.update_task(task_id, **updates)
        task = result['data']
        click.echo(f"Updated task: {task['id']}")
        click.echo(f"Title: {task['title']}")
        if task.get('description'):
            click.echo(f"Description: {task['description']}")
        click.echo(f"Status: {'Completed' if task['completed'] else 'Pending'}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('task_id')
@click.pass_context
def toggle(ctx, task_id):
    """Toggle task completion status."""
    client = ctx.obj['client']
    try:
        result = client.toggle_task(task_id)
        task = result['data']
        status = "completed" if task['completed'] else "pending"
        click.echo(f"Task {task['id']} marked as {status}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('task_id')
@click.confirmation_option(prompt='Are you sure you want to delete this task?')
@click.pass_context
def delete(ctx, task_id):
    """Delete a task."""
    client = ctx.obj['client']
    try:
        result = client.delete_task(task_id)
        click.echo(result['data']['message'])
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    cli()