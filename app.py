from flask import Flask,render_template,request,session,url_for,redirect,abort,jsonify
from google import genai
from google.genai import types
import sqlite3
import re
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


API_KEY = os.getenv("GEMINI_API_KEY")
VALID_USERNAME = os.getenv("USERNAME")
VALID_PASSWORD = os.getenv("PASS")

DATABASE = 'database.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authentication (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS userdetails (
                ph_num_or_mail TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES authentication(username)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES authentication(username)
            )
        ''')
        db.commit()

@app.route("/")
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html",validDetails = True)

@app.route("/login",methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")


        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM authentication WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        db.close()

        if user:
            session['username'] = user['username']
            return redirect(url_for('chat'))

        else:
            return render_template("login.html",error = "Invalid username or password")

    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        ph_num_or_mail = request.form['ph_num_or_mail']
        password = request.form['password']
        re_password = request.form['re_password']

        if not re.match(r'^[a-zA-Z-]+', username):
            return render_template('signup.html', error="Username can only contain characters and hyphens")
        if len(password) < 8:
            return render_template('signup.html', error="Password must be at least 8 characters long")
        if password != re_password:
            return render_template('signup.html', error="Passwords do not match")

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO authentication (username, password) VALUES (?, ?)", (username, password))
            cursor.execute("INSERT INTO userdetails (name, username, ph_num_or_mail) VALUES (?, ?, ?)", (name, username, ph_num_or_mail))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('signup.html', error="Username or Mobile/Email already exists")
        finally:
            db.close()
    return render_template('signup.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT role, content FROM chat_history WHERE username = ? ORDER BY timestamp", (session['username'],))
    chat_history = cursor.fetchall()
    db.close()

    return render_template('chatbot.html', chat_history=chat_history)

@app.route("/send_message",methods = ['POST'])
def send_message():
    if "username" not in session :
        return jsonify({'error': 'Unauthorized'}), 401
    
    if API_KEY is None:
        abort(500)

    prompt = request.form.get('prompt')
    username = session['username']

    if not prompt:
        return jsonify({'error': 'Message cannot be empty'}), 400

    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT role, content FROM chat_history WHERE username = ? ORDER BY timestamp DESC LIMIT 10", (username,))
    last_conversation = cursor.fetchall()
    

    try:
        client = genai.Client(api_key=API_KEY)
        file = request.files.get("file")

        if prompt or prompt.strip() != "":
            if file:
                binary_file = file.read()
                fileprompt = f"{prompt} File: {file.filename} "
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=binary_file,
                            mime_type='application/pdf',
                        ),
                        f"last conversation: {last_conversation} and prompt: {prompt}"
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction="Your are helpful assistant who generate response on prompt with analyzing the last conversation",
                    )
                )
                cursor.execute("INSERT INTO chat_history (username, role, content) VALUES (?, ?, ?)",(username, 'user', fileprompt))
                db.commit()
                
            else:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"last conversation: {last_conversation} and prompt: {prompt}",
                    config=types.GenerateContentConfig(
                        system_instruction="Your are helpful assistant who generate response on prompt with analyzing the last conversation",
                    )
                )
                cursor.execute("INSERT INTO chat_history (username, role, content) VALUES (?, ?, ?)",(username, 'user', prompt))
                db.commit()

            ai_response = format_gemini_response_to_html(response.text)
            cursor.execute("INSERT INTO chat_history (username, role, content) VALUES (?, ?, ?)",(username, 'model', ai_response))
            db.commit()
            db.close()
            return jsonify({'bot_response': ai_response})

    except (httpx.ConnectError, httpx.ReadTimeout) as e:
        db.close()
        return jsonify({'error': 'Network error, please try again later.'}), 500    

if __name__ == "__main__":
    init_db()
    app.run(debug = True)