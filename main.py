# ================== GPT PDF Q&A BOT ==================
# A Python desktop application to ask questions about PDFs or general topics.
# Powered by GPT models through OpenRouter API (Mistral-7B).
# Built with Tkinter for GUI and PyMuPDF for PDF text extraction.
# Author: Ayaan Nadeem | License: MIT

import os
import sys
import fitz
import requests
from dotenv import load_dotenv
from tkinter import filedialog, Tk, Label, Button, Text, END, Frame, PhotoImage
from tkinter.scrolledtext import ScrolledText

# === API CONFIGURATION ===
load_dotenv()
api_key = os.getenv("OPENROUTER_KEY")

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}" if api_key else "",
    "Content-Type": "application/json"
}

# === GLOBAL STATE ===
pdf_text = ""
pdf_loaded = False
notified_general_mode = False
PLACEHOLDER = "Type your question here..."
thinking_start_index = None

# === UTILITY FUNCTIONS ===
def resource_path(name: str) -> str:
    """Return absolute resource path for dev and PyInstaller builds."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, name)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), name)

def safe_photo(path, subsample=None):
    """Safely load PhotoImage; return 1x1 fallback if missing or invalid."""
    try:
        img = PhotoImage(file=path)
        if subsample:
            img = img.subsample(*subsample)
        return img
    except Exception:
        return PhotoImage(width=1, height=1)

# === PDF EXTRACTION ===
def extract_text_from_pdf(file_path):
    """Extract full text from a PDF file using PyMuPDF."""
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text() + "\n\n"
    except Exception as e:
        text = f"Error reading PDF: {e}"
    return text

# === GPT API CALL ===
def ask_gpt(question):
    """Send user question to GPT via OpenRouter API; include PDF context if loaded."""
    if pdf_loaded and pdf_text.strip():
        user_content = (
            "You are GPT. If the user asks about the document, answer using it. "
            "If the question is general, answer normally but you MAY reference the doc if relevant. "
            "Always provide a detailed explanation. Act like a human.\n\n"
            f"--- DOCUMENT START ---\n{pdf_text[:4000]}\n--- DOCUMENT END ---\n\n"
            f"User question: {question}"
        )
    else:
        user_content = (
            "You are GPT. Answer normally with details. No document is currently loaded.\n\n"
            f"User question: {question}"
        )

    messages = [
        {"role": "system", "content": "You are a helpful assistant named GPT."},
        {"role": "user", "content": user_content}
    ]
    data = {"model": "mistralai/mistral-7b-instruct", "messages": messages}

    try:
        res = requests.post(url, headers=headers, json=data, timeout=60)
    except Exception as e:
        return f"Network Error: {e}"

    if res.status_code == 200:
        try:
            return res.json()["choices"][0]["message"]["content"]
        except Exception:
            return "API response parsing error."
    else:
        return f"API Error {res.status_code}"

# === PDF LOADING ===
def load_pdf():
    """Open a PDF file, extract text, and update global state."""
    global pdf_text, pdf_loaded, notified_general_mode
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return

    txt = extract_text_from_pdf(file_path)
    if txt.startswith("Error"):
        pdf_text = ""
        pdf_loaded = False
        insert_system_message(txt, error=True)
    else:
        pdf_text = txt
        pdf_loaded = True
        insert_system_message(f"PDF loaded: {os.path.basename(file_path)}", success=True)

    notified_general_mode = False

# === QUESTION HANDLING ===
def send_question():
    """Handle user question input, show GPT response in chat."""
    global notified_general_mode, thinking_start_index
    question = input_box.get("1.0", END).strip()

    if not question or question == PLACEHOLDER:
        insert_system_message("Please type a question before asking GPT.", error=True)
        return

    if (not pdf_loaded) and (not notified_general_mode):
        insert_system_message("No PDF loaded — chatting in general mode.")
        notified_general_mode = True

    insert_chat_message(question, sender="user")
    thinking_start_index = chat_box.index(END)
    insert_chat_message("GPT is thinking...", sender="system")

    root.update_idletasks()
    answer = ask_gpt(question)

    if thinking_start_index is not None:
        chat_box.delete(thinking_start_index, END)
        thinking_start_index = None

    if answer.startswith("API Error") or answer.startswith("Network Error") or "parsing error" in answer:
        insert_system_message(answer, error=True)
    else:
        insert_chat_message(answer.strip(), sender="assistant")

    input_box.delete("1.0", END)

# === CHAT DISPLAY HELPERS ===
def insert_chat_message(text, sender="user"):
    """Insert chat message with appropriate image (user or GPT)."""
    if sender == "user":
        chat_box.insert(END, "\n")
        chat_box.image_create(END, image=img_user)
    elif sender == "assistant":
        chat_box.insert(END, "\n")
        chat_box.image_create(END, image=img_gpt)
    else:
        chat_box.insert(END, "\n")

    chat_box.insert(END, f" {text}\n\n")

def insert_system_message(text, success=False, error=False):
    """Insert system message with optional tick/cross icon."""
    if success:
        chat_box.image_create(END, image=img_tick)
    elif error:
        chat_box.image_create(END, image=img_cross)
    chat_box.insert(END, f" {text}\n\n")

def clear_input_on_click(event):
    """Clear placeholder text when input box is focused."""
    if input_box.get("1.0", END).strip() == PLACEHOLDER:
        input_box.delete("1.0", END)

# === GUI SETUP ===
root = Tk()
root.title("GPT PDF Q&A Bot")
root.geometry("800x700")
root.configure(bg="#0F172A")

# App icon for EXE and window
root.iconbitmap(resource_path("assets/gpt.ico"))

# Load images
img_user  = safe_photo(resource_path("assets/human.png"), (15, 15))
img_gpt   = safe_photo(resource_path("assets/gpt.png"), (15, 15))
img_tick  = safe_photo(resource_path("assets/tick.png"), (17, 17))
img_cross = safe_photo(resource_path("assets/cross.png"), (6, 6))

# Fonts and Colors
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_LABEL = ("Segoe UI", 13)
FONT_TEXT = ("Segoe UI", 11)

TITLE_BG = "#3B82F6"
TITLE_FG = "#FFFFFF"
CHAT_BG = "#1E293B"
CHAT_FG = "#F8FAFC"
INPUT_BG = "#334155"
INPUT_FG = "#F8FAFC"
BUTTON_BG = "#3B82F6"
BUTTON_FG = "#FFFFFF"

# Title Bar
Label(root, text="GPT PDF Q&A Bot", font=FONT_TITLE, bg=TITLE_BG, fg=TITLE_FG, pady=10).pack(fill="x")

# Main Frame
content_frame = Frame(root, bg="#0F172A")
content_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Buttons and Widgets
Button(content_frame, text="📄 Load PDF", command=load_pdf, width=18, bg=BUTTON_BG, fg=BUTTON_FG,
       font=("Segoe UI", 12, "bold"), relief="flat", activebackground="#2563EB").pack(pady=12)

chat_box = ScrolledText(content_frame, wrap="word", height=18, width=70,
                        bg=CHAT_BG, fg=CHAT_FG, font=FONT_TEXT, insertbackground="white")
chat_box.pack(padx=10, pady=10, anchor="center")

Label(content_frame, text="Enter your question:", font=FONT_LABEL, bg="#0F172A", fg="#F9FAFB").pack(pady=(5, 3))

input_box = Text(content_frame, height=4, width=70, bg=INPUT_BG, fg=INPUT_FG,
                 font=FONT_TEXT, insertbackground="white")
input_box.pack(padx=10, anchor="center")
input_box.insert("1.0", PLACEHOLDER)
input_box.bind("<FocusIn>", clear_input_on_click)

Button(content_frame, text="Ask GPT", command=send_question, width=20, bg=BUTTON_BG, fg=BUTTON_FG,
       font=("Segoe UI", 12, "bold"), relief="flat", activebackground="#2563EB").pack(pady=15, anchor="center")

# === START APP ===
if __name__ == "__main__":
    root.mainloop()
