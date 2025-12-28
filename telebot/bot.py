import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from google import genai

from prompts import SYSTEM_PROMPT, MODE_PROMPTS, PERSONALITY_PROMPTS
from memory import get_user, update_history

# LOAD ENV
load_dotenv()
BOT_TOKEN="7965397541:AAHhYEl4ElqO0XFZLo6CSJacInq11nUEkVM"
GOOGLE_API_KEY="AIzaSyD5iI_UX_TZEKFjRi9bRogfPaIk1oGgwuU"


# GEMINI CLIENT
client = genai.Client(api_key=GOOGLE_API_KEY)

# AI FUNCTION
import re

def extract_length_instruction(text: str):
    text = text.lower()

    # explicit line count
    match = re.search(r'(\d+)\s*lines?', text)
    if match:
        return f"Answer in exactly {match.group(1)} lines."

    if "short" in text:
        return "Answer in 2 to 3 lines only."

    if "long" in text or "detail" in text:
        return "Give a slightly detailed answer, but not too long."

    # default
    return "Answer briefly in 2 to 3 lines."

def ask_ai(user, message):
    # ----- LENGTH CONTROL -----
    length_instruction = "Give a concise answer in 3–4 lines."

    msg_lower = message.lower()
    if "short" in msg_lower:
        length_instruction = "Give a very short answer in 2 lines."
    elif "1 line" in msg_lower:
        length_instruction = "Answer in exactly 1 line."
    elif "2 line" in msg_lower:
        length_instruction = "Answer in exactly 2 lines."
    elif "5 line" in msg_lower:
        length_instruction = "Answer in exactly 5 lines."
    elif "brief" in msg_lower:
        length_instruction = "Keep the answer brief and to the point."

    convo = f"""
{SYSTEM_PROMPT}

Mode Instruction:
{MODE_PROMPTS[user["mode"]]}

Personality Instruction:
{PERSONALITY_PROMPTS[user["personality"]]}

Length Instruction:
{length_instruction}

Conversation:
"""

    for msg in user["history"][-6:]:  # last 6 msgs only
        role = "User" if msg["role"] == "user" else "Assistant"
        convo += f"{role}: {msg['content']}\n"

    convo += f"User: {message}\nAssistant:"

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=convo
    )

    return response.text.strip()



# COMMANDS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌌 CosmicLoveAI Activated\n\n"
        "/love /quantum /cosmos\n"
        "/soft /poetic /scientific /philosophical"
    )

async def set_mode(update, context, mode):
    user = get_user(update.effective_user.id)
    user["mode"] = mode

    starter = {
        "LOVE": "Tell me something beautiful about love.",
        "QUANTUM": "Explain quantum mechanics simply.",
        "COSMOS": "Tell me about the universe."
    }

    reply = ask_ai(user, starter[mode])
    update_history(user, "assistant", reply)

    await update.message.reply_text(reply)

async def set_personality(update, context, personality):
    user = get_user(update.effective_user.id)
    user["personality"] = personality
    await update.message.reply_text(f"Personality set to {personality}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    text = update.message.text

    update_history(user, "user", text)
    reply = ask_ai(user, text)
    update_history(user, "assistant", reply)

    await update.message.reply_text(reply)

# MAIN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("love", lambda u, c: set_mode(u, c, "LOVE")))
app.add_handler(CommandHandler("quantum", lambda u, c: set_mode(u, c, "QUANTUM")))
app.add_handler(CommandHandler("cosmos", lambda u, c: set_mode(u, c, "COSMOS")))

app.add_handler(CommandHandler("soft", lambda u, c: set_personality(u, c, "SOFT")))
app.add_handler(CommandHandler("poetic", lambda u, c: set_personality(u, c, "POETIC")))
app.add_handler(CommandHandler("scientific", lambda u, c: set_personality(u, c, "SCIENTIFIC")))
app.add_handler(CommandHandler("philosophical", lambda u, c: set_personality(u, c, "PHILOSOPHICAL")))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 CosmicLoveAI is running...")
app.run_polling()
