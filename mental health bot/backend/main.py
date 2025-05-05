from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging

from . import auth, gemini_chat
from .models import ChatMessageInput, ChatMessageOutput, UserInDB, ChatState
from .storage import chat_sessions # Simple in-memory session storage
from .core.config import settings # To ensure config is loaded

app = FastAPI(title="MindGuide AI")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mount static files (CSS, JS)
# Use correct relative path from 'main.py' to 'frontend/static'
app.mount("/static", StaticFiles(directory="./frontend/static"), name="static")

# Mount templates
# Use correct relative path from 'main.py' to 'frontend/templates'
templates = Jinja2Templates(directory="./frontend/templates")

# Include authentication router
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# --- Helper Function to Get/Create Chat State ---

def get_or_create_chat_state(username: str) -> ChatState:
    if username not in chat_sessions:
        # If no state exists, create a default one (but ideally start_chat should be called first)
        # This case might indicate starting mid-conversation, which we want to avoid.
        # A better approach is to ensure state is created ONLY on starting a new chat explicitly.
        # For now, let's assume state *should* exist if user is interacting post-login.
        logger.warning(f"Chat state not found for user {username}, creating default. Flow might be incorrect.")
        chat_sessions[username] = ChatState().model_dump() # Store as dict

    # Load state from storage and return as Pydantic model
    return ChatState(**chat_sessions[username])

def save_chat_state(username: str, state: ChatState):
    chat_sessions[username] = state.model_dump() # Save state back as dict

# --- API Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat/start", response_model=ChatMessageOutput)
async def start_chat_endpoint(current_user: UserInDB = Depends(auth.get_current_active_user)):
    """Endpoint to explicitly start a new chat session."""
    username = current_user.username
    logger.info(f"User '{username}' requesting to start a new chat.")

    # Call the function to get the initial AI message and state
    try:
        ai_message, new_state = await gemini_chat.start_new_chat(username)
        save_chat_state(username, new_state) # Save the newly created state
        return ChatMessageOutput(sender="ai", message=ai_message)
    except Exception as e:
        logger.error(f"Failed to start chat for user {username}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not start chat session.")


@app.post("/chat/message", response_model=ChatMessageOutput)
async def post_chat_message(
    chat_input: ChatMessageInput,
    current_user: UserInDB = Depends(auth.get_current_active_user)
):
    """Handles incoming user messages and returns AI response."""
    username = current_user.username
    user_message = chat_input.message

    # Get current chat state for the user
    try:
        current_state = get_or_create_chat_state(username) # Get state
         # Check if the chat was properly initialized
        if current_state.stage == "start" and not current_state.history:
             # This likely means /chat/start wasn't called or failed.
             # We could try calling start_new_chat here, but it's better handled client-side.
             logger.warning(f"User {username} sent message but chat not initialized. Responding with error.")
             # You could also try to initiate here, but it might confuse the flow.
             # ai_message, new_state = await gemini_chat.start_new_chat(username)
             # save_chat_state(username, new_state)
             # return ChatMessageOutput(sender="ai", message=ai_message)
             raise HTTPException(status_code=400, detail="Chat not properly started. Please refresh or restart.")

    except KeyError:
         # This handles the case where get_or_create_chat_state logic fails or isn't robust
         logger.error(f"Critical state error: Chat state missing for logged-in user {username}")
         raise HTTPException(status_code=500, detail="Chat session error. Please login again.")

    # Handle the message using the Gemini chat logic
    try:
        ai_response, updated_state = await gemini_chat.handle_chat_message(
            user_id=username,
            user_message=user_message,
            current_state=current_state
        )
        save_chat_state(username, updated_state) # Save the updated state
        return ChatMessageOutput(sender="ai", message=ai_response)
    except HTTPException as e:
        # Re-raise HTTP exceptions from gemini_chat (like 503)
        raise e
    except Exception as e:
        logger.error(f"Error handling chat message for user {username}: {e}", exc_info=True)
        # Don't save state if there was a major error during processing
        raise HTTPException(status_code=500, detail="Error processing message.")

# --- Health Check Route ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- Run with Uvicorn (for development) ---
# You would typically run this using: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
# The --reload flag watches for code changes.