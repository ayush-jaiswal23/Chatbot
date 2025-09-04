from flask import Flask,render_template,request,session,url_for,redirect,abort,jsonify
from google import genai
from google.genai import types
import os
import httpx
import markdown

def format_gemini_response_to_html(response_text: str) -> str:

    html_content = markdown.markdown(response_text, extensions=[
        'fenced_code',
        'nl2br',
        'tables',
        'attr_list',
        'md_in_html'
    ])

    formatted_html = f'<div class="chatbot-response">{html_content}</div>'

    return formatted_html


app = Flask(__name__)
app.secret_key = '_5#y2L"F4Q8z'

API_KEY = os.getenv("GOOGLE_API_KEY")
VALID_USERNAME = os.getenv("USERNAME")
VALID_PASSWORD = os.getenv("PASS")
chat_history = []
temp = []

@app.route("/")
def index():
    return render_template("login.html",validDetails = None)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html",validDetails = True)

@app.route("/auth/",methods = ['GET','POST'])
def authorization():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html",validDetails = False)

        if VALID_USERNAME.lower()==username.lower() and  VALID_PASSWORD==password :
            session["logged_in"] = True
            session["username"] = username.lower()
            return redirect(url_for("bot"))
        else:
            return render_template("login.html",validDetails = False)
    else:
        return render_template("login.html", validDetails=False)

def prompt_and_file_processing(client,prompt = None,file = None):
    if prompt or prompt.strip() != "":
        if file:
            binary_file = file.read()
            fileprompt = f"{prompt} File: {file.filename} "
            print(file)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=binary_file,
                        mime_type='application/pdf',
                    ),
                    f"last conversation: {chat_history} and prompt: {prompt}"
                ],
                config=types.GenerateContentConfig(
                    system_instruction="Your are helpful assistant who generate response on prompt with analyzing the last conversation",
                )
            )
            chat_history.append({"role": "user", "content": fileprompt})
            ai_response = format_gemini_response_to_html(response.text)
            chat_history.append({"role": "bot", "content": ai_response})

        else:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"last conversation: {chat_history} and prompt: {prompt}",
                config=types.GenerateContentConfig(
                    system_instruction="Your are helpful assistant who generate response on prompt with analyzing the last conversation",
                )
            )
            chat_history.append({"role": "user", "content": prompt})
            ai_response = format_gemini_response_to_html(response.text)
            chat_history.append({"role": "bot", "content": ai_response})

@app.route("/bot",methods = ['GET','POST'])
def bot():
    if "username" not in session or "logged_in" not in session:
        return render_template("login.html",validDetails = None)
    if API_KEY is None:
        abort(500)
    if request.method == 'POST':
        try:
            client = genai.Client(api_key=API_KEY)
            file = request.files["file"]
            prompt = request.form.get("prompt")

            prompt_and_file_processing(client=client, prompt=prompt, file=file)

            return redirect(url_for("bot"))

        except httpx.ConnectError as e:
            return f"No Internet {e}"

    else:
        return render_template("chatbot.html",chat_history = chat_history)

if __name__ == "__main__":
    app.run(debug = True)