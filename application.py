import os

from flask import Flask, render_template, redirect, url_for, flash, request
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename

from forms_fiels import *
from models import *

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = 'myfolder'


db = SQLAlchemy(app)

login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    
    return User.query.get(int(id))

@app.route("/", methods = ['GET', 'POST'])
def index():

    reg_form = Registration()

    if reg_form.validate_on_submit():
        
        username = reg_form.username.data
        password = reg_form.password.data

        hashed_password = pbkdf2_sha256.hash(password)

        user = User(username = username, password = hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Registered Successfully!!", 'success')

        return redirect(url_for('login'))

    return render_template('index.html', form = reg_form)

@app.route("/login", methods = ['GET', 'POST'])
def login():

    login_form = LoginForm()

    if login_form.validate_on_submit():
        
        user_object = User.query.filter_by(username = login_form.username.data).first()
        login_user(user_object)

        return redirect(url_for('main'))

    return render_template("login.html", form = login_form)


@app.route("/main", methods = ['GET', 'POST'])
#@login_required
def main():

    if not current_user.is_authenticated:

        flash("Please Login", 'danger')
        return redirect(url_for('login'))

    return render_template("main.html")

@app.route("/logout", methods = ['GET', 'POST'])
def logout():

    logout_user()
    flash("Logged out successfully!!", 'success')

    return redirect(url_for('login'))

ALLOWED_EXTENSIONS = set(['xlsx', 'csv'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/success', methods=['GET', 'POST'])
def success():

	if request.method == 'POST':

		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']

		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			flash('File successfully uploaded')
			return redirect('/main')
		else:
			flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
			return redirect(request.url)

if __name__ == "__main__":

    app.run(debug = True)