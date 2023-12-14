from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import request
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
    password="1055",
    database="notesdb1"
)

cursor = db.cursor()

# Check if the view exists
cursor.execute("SHOW TABLES LIKE 'email_view'")
view_exists = cursor.fetchone()

# Create the view if it doesn't exist
if not view_exists:
    cursor.execute("""
        CREATE VIEW email_view AS
        SELECT id, email, name
        FROM emails
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
    # Fetch email data
    cursor.execute("SELECT id, email, name FROM emails")
    email_data = cursor.fetchall()

    # Fetch note data
    user_id = current_user.id
    cursor.execute("SELECT note_id, content FROM notes WHERE user_id = %s", (user_id,))
    notes_data = cursor.fetchall()

    # Render the template with both email and note data
    return render_template('index.html', email_data=email_data, notes_data=notes_data)

@app.route('/add_email', methods=['GET', 'POST'])
@login_required
def add_email():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']

        cursor.execute("INSERT INTO emails (email, name) VALUES (%s, %s)", (email, name))
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

        cursor.execute("UPDATE emails SET email = %s, name = %s WHERE id = %s", (new_email, new_name, email_id))
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

@app.route('/notes')
@login_required
def notes():
    user_id = current_user.id
    cursor.execute("SELECT note_id, content FROM notes WHERE user_id = %s", (user_id,))
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

        cursor.execute("UPDATE notes SET content = %s WHERE note_id = %s", (new_content, note_id))
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

@app.route('/profile')
@login_required
def profile():
    # Fetch user profile data
    user_id = current_user.id
    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    # Render the profile template with user data
    return render_template('profile.html', user_data=user_data)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Handle profile editing logic here (e.g., update user information in the database)
        # ...

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    # Fetch user profile data
    user_id = current_user.id
    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    return render_template('edit_profile.html', user_data=user_data)


if __name__ == '__main__':
    app.run(debug=True)
