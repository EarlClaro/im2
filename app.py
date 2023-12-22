from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import request
from datetime import datetime

import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user
# Configure MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="July82001Cl@ro",
    database="notesdb2"
)

cursor = db.cursor()

# Check if the view exists
cursor.execute("SHOW TABLES LIKE 'email_view'")
view_exists = cursor.fetchone()

# Create the view if it doesn't exist
if not view_exists:
    cursor.execute("""
        CREATE VIEW email_view AS
        SELECT e.id, e.email, e.name, e.date_posted, u.username
        FROM emails e
        JOIN users u ON e.user_id = u.id
    """)
    db.commit()


# Routes for CRUD operations
@app.route('/')
def redirect_to_login():
    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT id, username FROM users WHERE username = %s AND password = %s", (username, password))
        user_data = cursor.fetchone()

        if user_data:
            user = User()
            user.id = user_data[0]
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/index')
@login_required
def index():
    # Fetch email data for the current user
    user_id = current_user.id

    # Fetch emails with date posted
    cursor.execute("SELECT id, email, name, date_posted FROM emails WHERE user_id = %s", (user_id,))
    email_data = cursor.fetchall()

    # Fetch notes with date posted
    cursor.execute("SELECT note_id, content, date_posted FROM notes WHERE user_id = %s", (user_id,))
    notes_data = cursor.fetchall()

    # Render the template with both email and note data
    return render_template('index.html', email_data=email_data, notes_data=notes_data)

@app.route('/add_email', methods=['GET', 'POST'])
@login_required
def add_email():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        user_id = current_user.id  # Get the current user's id

        cursor.execute("INSERT INTO emails (user_id, email, name) VALUES (%s, %s, %s)", (user_id, email, name))
        db.commit()

        flash('Email added successfully!', 'success')

        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit_email/<int:email_id>', methods=['GET', 'POST'])
@login_required
def edit_email(email_id):
    if request.method == 'POST':
        new_email = request.form['email']
        new_name = request.form['name']

        # Update the date_posted field to the current date and time
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            UPDATE emails 
            SET email = %s, name = %s, date_posted = %s 
            WHERE id = %s
        """, (new_email, new_name, current_date_time, email_id))
        db.commit()

        flash('Email updated successfully!', 'success')
        return redirect(url_for('index'))

    cursor.execute("SELECT id, email, name FROM emails WHERE id = %s", (email_id,))
    email_data = cursor.fetchone()

    return render_template('edit.html', email_data=email_data)

@app.route('/delete_email/<int:email_id>')
@login_required
def delete_email(email_id):
    cursor.execute("DELETE FROM emails WHERE id = %s", (email_id,))
    db.commit()

    flash('Email deleted successfully!', 'success')
    return redirect(url_for('index'))

# Update the 'notes' route
@app.route('/notes')
@login_required
def notes():
    user_id = current_user.id
    cursor.execute("SELECT note_id, content, date_posted FROM notes WHERE user_id = %s", (user_id,))
    notes_data = cursor.fetchall()
    return render_template('notes.html', notes_data=notes_data)

@app.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        content = request.form['note_content']  # Update to match the textarea name
        user_id = current_user.id

        cursor.execute("INSERT INTO notes (user_id, content) VALUES (%s, %s)", (user_id, content))
        db.commit()

        flash('Note added successfully!', 'success')
        
        # Redirect to the index route after adding a note
        return redirect(url_for('index'))

    return render_template('add_note.html')

@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    if request.method == 'POST':
        new_content = request.form['content']

        # Update the date_posted field to the current date and time
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            UPDATE notes 
            SET content = %s, date_posted = %s 
            WHERE note_id = %s
        """, (new_content, current_date_time, note_id))
        db.commit()

        flash('Note updated successfully!', 'success')
        return redirect(url_for('index'))

    cursor.execute("SELECT note_id, content FROM notes WHERE note_id = %s", (note_id,))
    note_data = cursor.fetchone()

    return render_template('edit_note.html', note_data=note_data)

@app.route('/delete_note/<int:note_id>')
@login_required
def delete_note(note_id):
    cursor.execute("DELETE FROM notes WHERE note_id = %s", (note_id,))
    db.commit()

    flash('Note deleted successfully!', 'success')
    return redirect(url_for('index'))

from flask import request

@app.route('/profile')
@login_required
def profile():
    # Fetch user profile data
    user_id = current_user.id
    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    # Fetch all user profiles
    cursor.execute("SELECT * FROM userprofile WHERE user_id = %s", (user_id,))
    user_profiles = cursor.fetchall()

    # Render the profile template with user data and profiles
    return render_template('profile.html', user_data=user_data, user_profiles=user_profiles)

# Edit the 'edit_profile' route
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Fetch user profile data
        user_id = current_user.id
        cursor.execute("SELECT * FROM userprofile WHERE user_id = %s", (user_id,))
        existing_profile = cursor.fetchone()

        # Get form data
        new_first_name = request.form['first_name']
        new_middle_name = request.form['middle_name']
        new_last_name = request.form['last_name']
        new_bio = request.form['bio']
        new_birthdate = request.form['birthdate']
        new_gender = request.form['gender']
        new_location = request.form['location']

        if existing_profile:
            # Update user profile data in 'userprofile' table
            cursor.execute("""
                UPDATE userprofile 
                SET first_name = %s, middle_name = %s, last_name = %s, bio = %s, birthdate = %s, gender = %s, location = %s
                WHERE user_id = %s
            """, (new_first_name, new_middle_name, new_last_name, new_bio, new_birthdate, new_gender, new_location, user_id))
        else:
            # Insert new user profile data into 'userprofile' table
            cursor.execute("""
                INSERT INTO userprofile (user_id, first_name, middle_name, last_name, bio, birthdate, gender, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, new_first_name, new_middle_name, new_last_name, new_bio, new_birthdate, new_gender, new_location))

        db.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    # Fetch user profile data
    user_id = current_user.id
    cursor.execute("SELECT * FROM userprofile WHERE user_id = %s", (user_id,))
    user_profile = cursor.fetchone()

    return render_template('edit_profile.html', user_profile=user_profile)




if __name__ == '__main__':
    app.run(debug=True)
