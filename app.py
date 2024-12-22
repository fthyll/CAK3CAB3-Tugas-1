from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kel2'  # Ganti dengan kunci rahasia yang aman
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Model Admin
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(150), nullable=False)

    @property
    def password(self):
        raise AttributeError('Password is not readable!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# Model Student
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Route untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.verify_password(password):
            login_user(admin)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password, please try again.', 'danger')
    return render_template('login.html')

# Route untuk logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Route untuk inisialisasi admin
@app.route('/init_admin')
def init_admin():
    admin = Admin(username='admin', password='admin')  # Hash otomatis
    db.session.add(admin)
    db.session.commit()
    return "Admin created with username 'admin' and password 'admin'."

# Route utama (halaman index)
@app.route('/')
@login_required
def index():
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

# Menambahkan data siswa
@app.route('/add', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    
    query = text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)")
    db.session.execute(query, {'name': name, 'age': age, 'grade': grade})
    db.session.commit()
    return redirect(url_for('index'))

# Menghapus data siswa
@app.route('/delete/<int:id>')
@login_required
def delete_student(id):
    query = text("DELETE FROM student WHERE id = :id")
    db.session.execute(query, {'id': id})
    db.session.commit()
    return redirect(url_for('index'))

# Mengedit data siswa
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        query = text("UPDATE student SET name = :name, age = :age, grade = :grade WHERE id = :id")
        db.session.execute(query, {'name': name, 'age': age, 'grade': grade, 'id': id})
        db.session.commit()
        return redirect(url_for('index'))
    else:
        query = text("SELECT * FROM student WHERE id = :id")
        student = db.session.execute(query, {'id': id}).fetchone()
        return render_template('edit.html', student=student)

# Main
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
