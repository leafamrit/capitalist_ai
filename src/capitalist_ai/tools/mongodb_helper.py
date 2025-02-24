import os
from typing import Dict, Any
from pymongo import MongoClient
from datetime import datetime

class MongoDBHelper:
    def __init__(self):
        """Initialize MongoDB connection using environment variables."""
        self.uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('MONGODB_DB', 'capitalist_ai')
        
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        
        # Initialize collections
        self.task_collection = self.db['task_outputs']
        self.conversation_collection = self.db['conversations']
        self.interaction_collection = self.db['interactions']

    def create_conversation(self, user_id: str) -> str:
        """
        Create a new conversation and return its ID.
        
        Args:
            user_id: Slack user ID
            
        Returns:
            str: Conversation ID
        """
        document = {
            'user_id': user_id,
            'start_time': datetime.utcnow(),
            'status': 'active'
        }
        result = self.conversation_collection.insert_one(document)
        return str(result.inserted_id)

    def store_conversation_state(self, conversation_id: str, user_id: str, state: Dict[str, Any]) -> str:
        """
        Store conversation state in MongoDB.
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: Slack user ID
            state: Current conversation state
            
        Returns:
            str: ID of the stored document
        """
        document = {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'state': state,
            'timestamp': datetime.utcnow()
        }
        
        result = self.conversation_collection.update_one(
            {'_id': conversation_id},
            {'$set': {
                'state': state,
                'last_updated': datetime.utcnow()
            }}
        )
        return conversation_id

    def log_interaction(self, conversation_id: str, user_id: str, message: str, event_type: str, step: int = None) -> str:
        """
        Log user interaction in MongoDB.
        
        Args:
            user_id: Slack user ID
            message: User's message or bot's response
            event_type: Type of event (e.g., 'user_message', 'bot_response', 'conversation_start')
            step: Current conversation step (optional)
            
        Returns:
            str: ID of the stored document
        """
        document = {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'message': message,
            'event_type': event_type,
            'step': step,
            'timestamp': datetime.utcnow()
        }
        
        result = self.interaction_collection.insert_one(document)
        return str(result.inserted_id)

    def store_task_output(self, conversation_id: str, user_id: str, task_name: str, output: str) -> str:
        """
        Store task output in MongoDB after converting to markdown.
        
        Args:
            task_name: Name of the task
            output: Task output text
            
        Returns:
            str: ID of the stored document
        """
        print("saving " + task_name)
        # Convert output to markdown if it's not already
        md_output = output
        if not output.startswith('#'):  # Basic check if it's not already markdown
            # Convert plain text to markdown
            md_output = f"# {task_name}\n\n{output}"
        
        document = {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'task_name': task_name,
            'output': md_output,
            'timestamp': datetime.utcnow(),
            'output_format': 'markdown'
        }
        
        result = self.task_collection.insert_one(document)
        return str(result.inserted_id)

    def get_task_output(self, task_name: str) -> Dict[str, Any]:
        """
        Retrieve the latest task output from MongoDB.
        
        Args:
            task_name: Name of the task
            
        Returns:
            Dict containing the task output document
        """
        return self.task_collection.find_one(
            {'task_name': task_name},
            sort=[('timestamp', -1)]
        )

    def close(self):
        """Close MongoDB connection."""
        self.client.close()
