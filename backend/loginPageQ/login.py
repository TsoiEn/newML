from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)

# Secret key for session management
app.secret_key = os.urandom(24)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'md'
app.config['MYSQL_PASSWORD'] = '(hC2T5Hm'
app.config['MYSQL_DB'] = 'patient_record'

# Initialize MySQL
mysql = MySQL(app)

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login/validatorlogin', methods=['POST'])
def validator_login():
    # Fetch form data
    username = request.form['username']
    password = request.form['password']

    # Validate credentials
    cursor = mysql.connection.cursor()  # No need to specify the cursorclass here
    cursor.execute('SELECT * FROM users WHERE email = %s', (username,))
    user = cursor.fetchone()

    if user:
        # Convert user data to a dictionary
        user = {
            "user_id": user[0],
            "name": user[1],
            "email": user[2],
            "signature": user[3]
        }

        # Check password hash
        if check_password_hash(user['signature'], password):
            # Set session variables
            session['logged_in'] = True
            session['user_id'] = user['user_id']
            session['username'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Replace with the actual dashboard route
        else:
            flash('Invalid username or password', 'danger')
    else:
        flash('User not found', 'danger')

    return redirect(url_for('login_page'))

@app.route('/logout', methods=['GET'])
def logout():
    # Clear session
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login_page'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Example placeholder route for logged-in users
    if 'logged_in' in session:
        return f"Welcome, {session['username']}!"
    else:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
