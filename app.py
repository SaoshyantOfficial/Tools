from flask import Flask, render_template, request, g, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
import sqlite3
from waitress import serve

app = Flask(__name__)
app.secret_key = '1236544'

UPLOAD_FOLDER = 'static/uploads'  # Name of the folder where uploaded images will be stored
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Accounting page settings

USERNAMES = {'yasin': 'bita', 'saleh': 'fatemeh', 'amir': 'adna', 'hamsara' : '1234'}

def get_db_accounting():
    """Get the SQLite database connection for the current thread."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(f'DataBases/Accounting/{session.get("username")}_expenses.db')
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY, topic varchar(50), value int(10))')
    return db


def fetch_expenses():
    """Function to sum expenses and retrieve expenses."""
    # Create the "expenses" table if it doesn't exist
    with get_db_accounting() as db:
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic VARCHAR(50) NOT NULL,
                value INT(10) NOT NULL
            )
        ''')

    # Retrieve expenses and calculate the total
    with get_db_accounting() as db:
        cursor = db.cursor()
        cursor.execute("SELECT ROWID, * FROM expenses ORDER BY id")  # Use ROWID as an alias for id
        expenses = cursor.fetchall()

        total = sum(expense[3] for expense in expenses)

        cursor.execute('SELECT topic, SUM(value) FROM expenses GROUP BY topic')
        unique_expenses = dict(cursor.fetchall())

    return expenses, total, unique_expenses


@app.teardown_appcontext
def close_db(exception):
    """Close the SQLite database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Main page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/accounting/login', methods=['GET', 'POST'])
def accounting_login():
    if request.method == 'POST':
        username = request.form.get('username')
        session["username"] = username
        password = request.form.get('password')
        if username in USERNAMES and USERNAMES[username] == password:
            expenses, total, unique_expenses = fetch_expenses()
            return render_template('accounting.html', expenses=expenses, total=total,
                                   unique_expenses=unique_expenses)
        else:
            flash("Invalid username or password", "error")
    return render_template('accountingLogin.html')


@app.route('/add', methods=['POST'])
def add_expense():
    # Get the topic and value inputs from the form
    topic = request.form['topic']
    value = int(request.form['value'])

    # Insert the expense into the database
    with get_db_accounting() as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO expenses (topic, value) VALUES (?, ?)", (topic, value))
        db.commit()

    # Retrieve expenses and total
    expenses, total, unique_expenses = fetch_expenses()

    return render_template('accounting.html', expenses=expenses, total=total, unique_expenses=unique_expenses)


@app.route('/remove/<id>', methods=['POST'])
def remove_expense(id):
    with get_db_accounting() as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM expenses WHERE ROWID=?", (id,))  # Use ROWID as an alias for id

        # Reorganize the ROWIDs to start from 1
        cursor.execute("UPDATE expenses SET ROWID = ROWID - 1 WHERE ROWID > ?", (id,))
        db.commit()

    # Retrieve expenses and total
    expenses, total, unique_expenses = fetch_expenses()
    return render_template('accounting.html', expenses=expenses, total=total, unique_expenses=unique_expenses)




# TO-DO List settings

def connect_db():
    conn = sqlite3.connect(f'DataBases/ToDoList/{session.get("username")}_TodoList.db')
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_activities
                    (id INTEGER PRIMARY KEY, activity text, completed INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS weekly_activities
                    (id INTEGER PRIMARY KEY, activity text, completed INTEGER)''')
    return conn
    

def fetch_activities():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_activities")
        daily_activities = cursor.fetchall()

        cursor.execute("SELECT * FROM weekly_activities")
        weekly_activities = cursor.fetchall()

    return daily_activities, weekly_activities


@app.route('/todoList/login', methods=['GET', 'POST'])
def todo_list_login():
    if request.method == 'POST':
        username = request.form.get('username')
        session["username"] = username
        password = request.form.get('password')
        if username in USERNAMES and USERNAMES[username] == password:
            daily_activities, weekly_activities = fetch_activities()
            return render_template('todo-list.html', daily_activities=daily_activities, weekly_activities=weekly_activities)
        else:
            flash("Invalid username or password", "error")
    return render_template('todoListLogin.html')

@app.route('/daily', methods=['GET', 'POST'])
def daily():
    if request.method == 'POST':
        activity = request.form['daily_activity']
        completed = 0  # Initialize completed as False
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO daily_activities(activity, completed) VALUES (?, ?)", (activity, completed))

    daily_activities, weekly_activities = fetch_activities()
    return render_template('todo-list.html', daily_activities=daily_activities, weekly_activities=weekly_activities)

@app.route('/weekly', methods=['GET', 'POST'])
def weekly():
    if request.method == 'POST':
        activity = request.form['weekly_activity']
        completed = 0  # Initialize completed as False
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO weekly_activities(activity, completed) VALUES (?, ?)", (activity, completed))

    daily_activities, weekly_activities = fetch_activities()
    return render_template('todo-list.html', daily_activities=daily_activities, weekly_activities=weekly_activities)

@app.route('/daily_complete/<int:index>')
def daily_complete(index):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE daily_activities SET completed = 1 - completed WHERE id=?', (index,))
    return redirect('/daily')

@app.route('/daily_delete/<int:index>')
def daily_delete(index):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_activities WHERE id=?", (index,))
        cursor.execute("UPDATE daily_activities SET id=id-1 WHERE id > ?", (index,))

    return redirect('/daily')

@app.route('/weekly_complete/<int:index>')
def weekly_complete(index):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE weekly_activities SET completed = 1 - completed WHERE id=?', (index,))
    return redirect('/weekly')

@app.route('/weekly_delete/<int:index>')
def weekly_delete(index):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weekly_activities WHERE id=?", (index,))
        cursor.execute("UPDATE weekly_activities SET id=id-1 WHERE id > ?", (index,))
    return redirect('/weekly')






# Storage page


def create_table():
    conn = sqlite3.connect(f'DataBases/Storage/{session.get("username")}_storage.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS images
                      (id INTEGER PRIMARY KEY, description TEXT, filename TEXT)''')
    conn.commit()
    conn.close()

def insert_image(description, filename):
    conn = sqlite3.connect(f'DataBases/Storage/{session.get("username")}_storage.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO images (description, filename) VALUES (?, ?)', (description, filename))
    conn.commit()
    conn.close()

def get_all_images():
    conn = sqlite3.connect(f'DataBases/Storage/{session.get("username")}_storage.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM images')
    images = cursor.fetchall()
    conn.close()
    return images

@app.route('/storage/login', methods=['GET', 'POST'])
def storage_login():
    if request.method == 'POST':
        username = request.form.get('username')
        session["username"] = username
        password = request.form.get('password')

        if username in USERNAMES and USERNAMES[username] == password:
            create_table()
            images = get_all_images()
            return render_template('storage.html', images=images)
        else:
            flash("Invalid username or password", "error")
    return render_template('storageLogin.html')

@app.route('/storage', methods=['GET', 'POST'])
def storage():
    if request.method == 'POST':
        description = request.form['description']
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            insert_image(description, filename)
            return redirect(url_for('storage'))

    images = get_all_images()
    return render_template('storage.html', images=images)

@app.route('/delete/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    conn = sqlite3.connect(f'DataBases/Storage/{session.get("username")}_storage.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM images WHERE id = ?', (image_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('storage'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}




# Records Page

DATABASE = 'records.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(f'DataBases/Records/{session.get("username")}_records.db')
        db.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/records/login', methods=['GET', 'POST'])
def records_login():
    if request.method == 'POST':
        username = request.form.get('username')
        session["username"] = username
        password = request.form.get('password')

        if username in USERNAMES and USERNAMES[username] == password:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM records')
            records = cursor.fetchall()
            return render_template('records.html', records=records)
        else:
            flash("Invalid username or password", "error")

    return render_template('recordsLogin.html')

@app.route('/records/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        description = request.form['description']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO records (username, password, description) VALUES (?, ?, ?)', (username, password, description))
        db.commit()
        return redirect(url_for('add'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM records')
    records = cursor.fetchall()
    return render_template('records.html', records=records)

@app.route('/records/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    if 'username' not in session:
        return redirect(url_for('records_login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM records WHERE id = ?', (record_id,))
    db.commit()
    return redirect(url_for('add'))

if __name__ == '__main__':
    app.run(debug=True)
    # serve(app, host='0,0,0,0', port=5000)