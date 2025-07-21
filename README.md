# PDFQnABot
AI-powered desktop chatbot (ChatGPT-style) with optional PDF Q&A — built with **Python, Tkinter, and OpenRouter APIs**.

---

## Features
- **Chat Freely:** Use it like ChatGPT — ask anything, get instant AI responses.
- **PDF Q&A:** Upload a PDF, and the bot will answer questions based on its content.
- **User-Friendly UI:** Built with **Tkinter**, designed for smooth interaction.
- **Mistral AI Model:** Powered by **Mistral via OpenRouter API** for accurate responses.
- **Lightweight & Offline-Friendly UI:** No heavy dependencies — just plug and play.

---

## Tech Stack
- **Language:** Python 3
- **Libraries:** Tkinter (built-in with Python), Requests, PyMuPDF, Python-Dotenv
- **AI Model:** Mistral (via OpenRouter API)

---

## Screenshots
**App Startup:**  
![App Screenshot 1](assets/screenshot1.png)

**Chat with PDF:**  
![App Screenshot 2](assets/screenshot2.png)

---

## How to Run
1. **Clone the repo:**
   ```bash
   git clone https://github.com/AyaanNadeem12/PDFQnABot.git
   ```
2. **Install dependencies from requirements.txt:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Tkinter is built-in with Python. If missing, install it via your OS package manager.*

3. **Set your API key:**
   - Create a `.env` file in the project folder.
   - Add the following line to it:
     ```env
     OPENROUTER_KEY=your_api_key_here
     ```

4. **Run the app:**
   ```bash
   python main.py
   ```

---

## Roadmap
- [ ] Add Dark Mode UI
- [ ] Support Multiple PDFs
- [ ] Add Model Selection (OpenAI, Gemini)

---

## License
This project is open-source and available under the [MIT License](LICENSE).
