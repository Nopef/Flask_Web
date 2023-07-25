from flask import Flask, request, url_for,session,render_template,redirect,flash,send_from_directory
from werkzeug.utils import secure_filename
import re
import os
from flask_mysqldb import MySQL
import MySQLdb.cursors


app = Flask(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = "abobich228"
app.config["MYSQL_HOST"] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "aboba"
app.config["MYSQL_DB"] = "flask_web"
app.config["UPLOAD_FOLDER"] = r"C:\Users\danys\Desktop\Web-Project\Files"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods=["GET", "POST"])
def login():
    message = ''
    if request.method == "POST" and "password" in request.form and "email" in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print("cursor")
        cursor.execute("SELECT * FROM user WHERE email=%s and password=%s",
                       (email,password))
        user = cursor.fetchone()
        if user:
            session['name'] = user['name']
            session['loggedin'] = True
            session['email'] = user['email']
            message = "Success"
            return redirect(url_for('profile'))
        else:
            message = "Incorret"
    return render_template("login.html",message=message)
@app.route("/register",methods=["GET",'POST'])
def register():
    message = ''
    if request.method == "POST" and "password" in request.form and "email" in request.form and "name" in request.form:
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE email=%s",(email,))
        user = cursor.fetchone()
        if user:
            message = "user already exist"
            return render_template("register.html",message=message)
        else:
            cursor.execute("INSERT INTO user VALUES (NULL,%s,%s,%s)",(username,email,password))
            mysql.connection.commit()
            session['name'] = username
            session['loggedin'] = True
            session['email'] = email
            message = "Success"
            return redirect(url_for('profile'))
    return render_template('register.html',message=message)
@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    session.pop('name',None)
    return redirect(url_for("login"))
@app.route("/profile")
def profile():
    if "loggedin" in session and session['loggedin']:
        return render_template("user.html")
    else:
        return redirect(url_for("login"))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/profile/upload",methods=["GET","POST"])
def upload():
    if "loggedin" in session and session['loggedin']:
        if request.method == "POST":
            if 'file' not in request.files:
                flash("Select File dude...")
                return(redirect(request.url))
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and file.content_length > 0 and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('download',name=filename))
            else:
                flash("Invalid. Kto blyat")
                return redirect(url_for('upload'))
        else:
            return redirect(url_for('profile'))
    else:
        return redirect(url_for("login"))

@app.route("/Files/<name>")
def download(name):
    if "loggedin" in session and session['loggedin']:
        return send_from_directory(app.config['UPLOAD_FOLDER'],name)
