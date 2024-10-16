from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simulating Admin User (for simplicity)
ADMIN_USER = {'username': 'admin', 'password': 'password123'}

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    if user_id == '1':  # The only user is admin with ID 1
        return User(id='1')
    return None

# Database setup
def init_db():
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            review TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home route with form
@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        review = request.form['review']

        # Validate fields
        if not name or not phone or not email or not review:
            flash('Please fill in all the fields!', 'error')
            return redirect(url_for('index'))

        # Store in database
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO reviews (name, phone, email, review) VALUES (?, ?, ?, ?)',
                       (name, phone, email, review))
        conn.commit()
        conn.close()

        flash('Review submitted successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('index.html')


@app.route('/')
def index():
    return render_template('index.html')

# Admin login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check credentials
        if username == ADMIN_USER['username'] and password == ADMIN_USER['password']:
            user = User(id='1')
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials. Try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin route to view submissions (protected by login)
@app.route('/admin')
@login_required
def admin():
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reviews')
    all_reviews = cursor.fetchall()
    conn.close()

    return render_template('admin.html', reviews=all_reviews)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True,port=5050)
