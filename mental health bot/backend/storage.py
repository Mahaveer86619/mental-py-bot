# In-memory storage (for demonstration purposes ONLY)
# Replace with a database in a real application!

# { "username": {"hashed_password": "...", "email": "...", "full_name": "..."} }
users_db = {}

# { "username": {"stage": "...", "condition": "...", "history": []} }
# Stages: "start", "get_condition", "get_personal_info", "assessment", "report", "done"
chat_sessions = {}