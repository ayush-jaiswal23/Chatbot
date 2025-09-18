# Serenity - A Conversational AI Chatbot

Serenity is a web-based chatbot application powered by the Gemini API. It provides a user-friendly interface for engaging in conversations with a powerful language model. The application includes user authentication, chat history, and the ability to upload files for context-aware conversations.

## Features

- **User Authentication**: Secure user registration and login system.
- **Chat Interface**: A clean and intuitive interface for interacting with the chatbot.
- **Chat History**: Your conversations are saved and displayed, allowing you to continue where you left off.
- **File Upload**: Upload PDF files to provide context for your conversations.
- **Markdown Support**: The chatbot's responses are rendered with Markdown for better formatting.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Database**: SQLite
- **AI Model**: Google Gemini
- **Libraries**:
    - `google-generativeai`: To interact with the Gemini API.
    - `Flask`: For the web framework.
    - `httpx`: For making HTTP requests.
    - `Markdown`: To parse and render Markdown in responses.
    - `python-dotenv`: To manage environment variables.

## Setup and Installation

To run this project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ayush-jaiswal23/Chatbot.git
   cd Chatbot
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory of the project and add your Gemini API key:
   ```
   GEMINI_API_KEY="your_gemini_api_key"
   ```

5. **Initialize the database**:
   The database will be automatically initialized when you run the application for the first time.

6. **Run the application**:
   ```bash
   python app.py
   ```

   The application will be available at `http://127.0.0.1:5000`.

## Usage

1. **Sign up**: Create a new account or log in if you already have one.
2. **Chat**: Once logged in, you can start chatting with Serenity.
3. **Upload Files**: Click the "add file" button to upload a PDF file. The chatbot will use the file's content as context for the conversation.
