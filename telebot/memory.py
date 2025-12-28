user_memory = {}

def get_user(user_id):
    if user_id not in user_memory:
        user_memory[user_id] = {
            "mode": "AUTO",
            "personality": "SOFT",
            "history": []
        }
    return user_memory[user_id]

def update_history(user, role, content):
    user["history"].append({"role": role, "content": content})
    user["history"] = user["history"][-5:]  # keep last 5
