from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

users = {}  

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.reminders = []  
        self.moods = []     

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == user_id:
            return user
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/meditation')
def meditation():
    return render_template('meditation.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        flash(f"Thank you, {name}. Your message has been received.", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('reminders'))
        else:
            flash('Login failed. Please check your username or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        if username in users:
            flash('Username already exists.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(id=str(len(users) + 1), username=username, password=hashed_pw)
            users[username] = new_user
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/reminders', methods=['GET', 'POST'])
@login_required
def reminders():
    if request.method == 'POST':
        reminder_text = request.form.get('reminder')
        reminder_time = request.form.get('reminder_time')

        if reminder_text:
            current_user.reminders.append({
                'text': reminder_text,
                'time': reminder_time
            })
            flash('Reminder added!', 'success')

    return render_template('reminders.html', reminders=current_user.reminders)


@app.route('/edit_reminder/<int:index>', methods=['GET', 'POST'])
@login_required
def edit_reminder(index):
    try:
        reminder = current_user.reminders[index]
    except IndexError:
        flash("Reminder not found.", "danger")
        return redirect(url_for('reminders'))

    if request.method == 'POST':
        new_text = request.form['reminder']
        current_user.reminders[index]['text'] = new_text
        flash("Reminder updated!", "success")
        return redirect(url_for('reminders'))

    return render_template('edit_reminder.html', reminder=reminder, index=index)

@app.route('/delete_reminder/<int:index>')
@login_required
def delete_reminder(index):
    try:
        current_user.reminders.pop(index)
        flash("Reminder deleted!", "success")
    except IndexError:
        flash("Reminder not found.", "danger")
    return redirect(url_for('reminders'))

@app.route('/mood', methods=['GET', 'POST'])
@login_required
def mood():
    if request.method == 'POST':
        mood = request.form['mood']
        date = request.form['date']
        if mood and date:
            current_user.moods.append({'date': date, 'mood': mood})
            flash('Mood entry added!', 'success')
    return render_template('mood.html', moods=current_user.moods)


if __name__ == '__main__':
    if not users:
        test_user = User(id="1", username="testuser", password=generate_password_hash("password"))
        users["testuser"] = test_user
    app.run(debug=True)

