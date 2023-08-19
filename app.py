from flask import Flask, render_template, request, g, redirect, url_for, session, flash
import sqlite3
from waitress import serve

app = Flask(__name__)
app.secret_key = '1236544'

# Accounting page settings

ACCOUNTING_DATABASE = 'expenses.db'
USERNAMES = {'yasin': 'bita', 'saleh': 'barin', 'amir': 'adna', 'hamsara' : '1234'}

def get_db():
    """Get the SQLite database connection for the current thread."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(f'DataBases/Accounting/{session.get("username")}_expenses.db')
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY, topic varchar(50), value int(10))')
    return db


def fetch_expenses():
    """function to sum expenses and retrieve expenses"""
    # Retrieve expenses and calculate the total
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY id")
        expenses = cursor.fetchall()

        total = sum(expense[2] for expense in expenses)

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
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO expenses (topic, value) VALUES (?, ?)", (topic, value))
        db.commit()

    # Retrieve expenses and total
    expenses, total, unique_expenses = fetch_expenses()

    return render_template('accounting.html', expenses=expenses, total=total, unique_expenses=unique_expenses)


@app.route('/remove/<id>', methods=['POST'])
def remove_expense(id):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
        cursor.execute("UPDATE expenses SET id=id-1 WHERE id > ?", (id,))
        db.commit()

    # Retrieve expenses and total
    expenses, total, unique_expenses = fetch_expenses()
    return render_template('accounting.html', expenses=expenses, total=total, unique_expenses=unique_expenses)


# TO-DO List settings

def fetch_activities():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activities")
        activities = cursor.fetchall()

    return activities


@app.route('/todoList/login', methods=['GET', 'POST'])
def todo_list_login():
    if request.method == 'POST':
        username = request.form.get('username')
        session["username"] = username
        password = request.form.get('password')
        if username in USERNAMES and USERNAMES[username] == password:
            activities = fetch_activities()
            return render_template('todo-list.html', activities=activities)
        else:
            flash("Invalid username or password", "error")
    return render_template('todoListLogin.html')


def connect_db():
    conn = sqlite3.connect(f'DataBases/ToDoList/{session.get("username")}_TodoList.db')
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS activities
                    (id INTEGER PRIMARY KEY, activity text, completed INTEGER)''')
    return conn


@app.route('/todo-list', methods=['GET', 'POST'])
def todo_list():
    if request.method == 'POST':
        activity = request.form['activity']
        completed = 0  # Initialize completed as False
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO activities(activity, completed) VALUES (?, ?)", (activity, completed))

    activities = fetch_activities()
    return render_template('todo-list.html', activities=activities)


@app.route('/complete/<int:index>')
def complete(index):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE activities SET completed = 1 - completed WHERE id=?', (index,))
    return redirect('/todo-list')


@app.route('/delete/<int:index>')
def delete(index):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id=?", (index,))
        cursor.execute("UPDATE activities SET id=id-1 WHERE id > ?", (index,))

    return redirect('/todo-list')


if __name__ == '__main__':
    # app.run(debug=True)
    serve(app, host='0.0.0.0', port=80)
