#!/usr/bin/env python
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from slack_bolt import App
from collections import defaultdict
from slack_bolt.adapter.fastapi import SlackRequestHandler
from capitalist_ai.crew import CapitalistAI
from capitalist_ai.tools.mongodb_helper import MongoDBHelper
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize MongoDB helper
mongodb = MongoDBHelper()

def load_task_files(conversation_id: str, user_id: str):
    """Read all task.md files from project root and store in MongoDB"""
    task_files = [f for f in os.listdir() if f.endswith('_task.md')]
    for task_file in task_files:
        try:
            with open(task_file, 'r') as f:
                content = f.read()
                task_name = task_file.replace('_task.md', '')
                mongodb.store_task_output(conversation_id, user_id, task_name, content)
        except Exception as e:
            print(f"Error loading task file {task_file}: {str(e)}")

# Initialize FastAPI app
app = FastAPI(title="Capitalist AI Slack Bot")

# Initialize Slack app
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)
handler = SlackRequestHandler(slack_app)

# Conversation state management
conversation_state = defaultdict(lambda: {"step": 0, "data": {}, "conversation_id": None})

# Define questions for the conversation flow
QUESTIONS = [
    "please provide the URL to your brand positioning document",
    "please provide the URL to your product backlog document",
    "please provide the URL to your KPI document",
    "please provide the URL to your investor meeting notes",
    "please provide the URL to your website",
    "please provide the URL to your pricing page"
]

def get_next_question(user_id: str) -> Optional[str]:
    """Get the next question in the conversation flow"""
    
    state = conversation_state[user_id]
    # Log the current state
    mongodb.log_interaction(
        conversation_id=state["conversation_id"],
        user_id=user_id,
        message=f"Current step: {state['step']}",
        event_type='step_check',
        step=state["step"]
    )
    if state["step"] < len(QUESTIONS):
        return QUESTIONS[state["step"]]
    return None

def process_response(user_id: str, response: str) -> str:
    """Process user response and return next action"""
    state = conversation_state[user_id]
    
    # Extract URL from the response
    # Format example: "<@U08EC1XL98E> <https://pictory.ai/>" -> "https://pictory.ai/"
    import re
    urls = re.findall(r'<(https?://[^>]+)>', response)
    url = urls[0] if urls else response  # fallback to original response if no URL found
    
    # Store the extracted URL
    state["data"][f"question_{state['step']}"] = url
    state["step"] += 1
    
    # Check if we have more questions
    next_question = get_next_question(user_id)
    if next_question:
        return next_question
    
    # If no more questions, process all collected data
    collected_data = state["data"]
    
    # Store final conversation state before deletion
    mongodb.store_conversation_state(state["conversation_id"], user_id, state)
    del conversation_state[user_id]
    
    crew_inputs = {
        "positioning": collected_data["question_0"],
        "productbacklog": collected_data["question_1"],
        "KPIdoc": collected_data["question_2"],
        "investor_meeting_notes": collected_data["question_3"],
        "website": collected_data["question_4"],
        "pricing": collected_data["question_5"]
    }

    ## TESTING:
    # crew_inputs = {
    #     "positioning": "https://docs.google.com/document/d/1kayH3AXm915h-ZI6Wp8juRQLZ225V2BRClAJInofz-0/edit?usp=sharing",
    #     "productbacklog": "https://feedback.pictory.ai/roadmap",
    #     "KPIdoc": "https://docs.google.com/spreadsheets/d/1kN3cFKFdWawH2SGE9pQSh8zmO6zsjewQWByI9Bx2FkQ/edit?usp=sharing",
    #     "investor_meeting_notes": "https://docs.google.com/document/d/1nbHBmsLFGyLtD_DzG5qlx2T1nQjg_emDwfi5oYwjlUo/edit?usp=sharing",
    #     "website": "https://pictory.ai/",
    #     "pricing": "https://pictory.ai/pricing"
    # }

    # Create a new CapitalistAI instance with all collected data
    result = CapitalistAI(crew_inputs).crew().kickoff(inputs=crew_inputs)
    # result = "k"
    
    # Load task files on startup
    load_task_files(state["conversation_id"], user_id)

    # Log the final result
    mongodb.log_interaction(
        conversation_id=state["conversation_id"],
        user_id=user_id,
        message=str(result),
        event_type='final_result'
    )
    
    return str(result) + ".\n\n Visit https://capitalist-orator.vercel.app/?conv_id=" + state["conversation_id"] + " to talk with me in more detail."

@app.post("/slack/events")
async def endpoint(req: Request):
    """Handle incoming Slack events"""
    return await handler.handle(req)

@slack_app.event("app_mention")
def handle_mention(event: Dict[str, Any], say: callable):
    """Handle when the bot is mentioned in a channel"""
    # Ignore messages from the bot itself
    if event.get("user") and not event.get("bot_id"):
        try:
            user_id = event["user"]
            message = event["text"]
            
            # Log the incoming message
            mongodb.log_interaction(
                conversation_id=conversation_state[user_id].get("conversation_id"),
                user_id=user_id,
                message=message,
                event_type='user_message'
            )

            # If this is the start of a conversation
            if message.strip().split(" ")[-1].lower() in ["start", "begin", "hi", "hello"]:
                # Initialize conversation with new conversation ID
                conversation_id = mongodb.create_conversation(user_id)
                conversation_state[user_id] = {"step": 0, "data": {}, "conversation_id": conversation_id}
                # Log conversation start
                mongodb.log_interaction(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    message="Starting new conversation",
                    event_type='conversation_start'
                )
                first_question = get_next_question(user_id)
                say(f"Hello! Let's get started. {first_question}")
                return

            # Process the response and get next action
            mongodb.log_interaction(
                conversation_id=conversation_state[user_id].get("conversation_id"),
                user_id=user_id,
                message="Continuing conversation",
                event_type='conversation_continue'
            )
            response = process_response(user_id, message)
            # Log bot's response
            mongodb.log_interaction(
                conversation_id=conversation_state[user_id].get("conversation_id"),
                user_id=user_id,
                message=response,
                event_type='bot_response'
            )
            say(response)
            
        except Exception as e:
            # Log error
            error_user_id = event.get("user", "unknown")
            error_conversation_id = conversation_state.get(error_user_id, {}).get("conversation_id")
            mongodb.log_interaction(
                conversation_id=error_conversation_id,
                user_id=error_user_id,
                message=str(e),
                event_type='error'
            )
            say(f"Sorry, I encountered an error: {str(e)}")

@slack_app.event("message")
def handle_message(event: Dict[str, Any], say: callable):
    """Handle direct messages to the bot"""
    # Ignore messages from the bot itself
    if event.get("user") and not event.get("bot_id"):
        try:
            user_id = event["user"]
            message = event["text"]
            
            # Log the incoming message
            mongodb.log_interaction(
                conversation_id=conversation_state[user_id].get("conversation_id"),
                user_id=user_id,
                message=message,
                event_type='user_message'
            )

            # If this is the start of a conversation
            if message.strip().split(" ")[-1].lower() in ["start", "begin", "hi", "hello"]:
                # Initialize conversation with new conversation ID
                conversation_id = mongodb.create_conversation(user_id)
                conversation_state[user_id] = {"step": 0, "data": {}, "conversation_id": conversation_id}
                # Log conversation start
                mongodb.log_interaction(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    message="Starting new conversation",
                    event_type='conversation_start'
                )
                first_question = get_next_question(user_id)
                say(f"Hello! Let's get started. {first_question}")
                return

            # Process the response and get next action
            mongodb.log_interaction(
                conversation_id=conversation_state[user_id].get("conversation_id"),
                user_id=user_id,
                message="Continuing conversation",
                event_type='conversation_continue'
            )
            response = process_response(user_id, message)
            # Log bot's response
            mongodb.log_interaction(
                conversation_id=conversation_state[user_id].get("conversation_id"),
                user_id=user_id,
                message=response,
                event_type='bot_response'
            )
            say(response)
            
        except Exception as e:
            # Log error
            error_user_id = event.get("user", "unknown")
            error_conversation_id = conversation_state.get(error_user_id, {}).get("conversation_id")
            mongodb.log_interaction(
                conversation_id=error_conversation_id,
                user_id=error_user_id,
                message=str(e),
                event_type='error'
            )
            say(f"Sorry, I encountered an error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    mongodb.close()

def serve():
    """Entry point for running the server"""
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "capitalist_ai.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

if __name__ == "__main__":
    serve()
