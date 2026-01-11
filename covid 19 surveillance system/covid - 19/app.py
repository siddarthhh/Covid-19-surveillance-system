from json import dumps
from wsgiref.util import request_uri
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for , flash
import os
from werkzeug.utils import secure_filename
import shutil
import fnmatch
from datetime import datetime
from pytz import timezone
from resources.main_video import suspect_name
import cv2


app = Flask(__name__)
app.config['MONGO_URI']="url"
mongo=PyMongo(app)

app.secret_key = "secret key"
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
SUSPECT_FOLDER = os.path.join(path, 'suspects')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SUSPECT_FOLDER'] = SUSPECT_FOLDER
original = r"C:\Users\Rinku\Downloads\login\login\uploads"
target = r'C:\Users\Rinku\Downloads\login\login\images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route('/user_register', methods=['POST','GET'])
def user_register():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        firstName = request.form.get('firstName')
        lastName = request.form.get('secondName')
        phoneNo = request.form.get('phoneNo')
        address = request.form.get('address')
        email = request.form.get('email')
        birthDate = request.form.get('birthDate')
        gender = request.form.get('Gender')
        img = request.form.get('image')
       
        if 'files[]' in request.files:
            files = request.files.get('files[]') 
            mongo.save_file(files.filename, files)  
            mongo.db.user_details.insert_one({'fname':firstName,'lname':lastName,'phone':phoneNo,'address':address,'email':email,'dob':birthDate,'gender':gender,'file_name' : files.filename, 'image':img})
    pattern = filename
    flash(pattern)
    src_files = os.listdir(original)
    for file_name in src_files:
        if fnmatch.fnmatch(file_name,pattern)==True:
            full_file_name= os.path.join(original,file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name,target)

    return redirect(url_for('home'))

@app.route('/registration')
def registration():
    return render_template('registration.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/attendance', methods=['POST', 'GET'])
def attendance():
    return render_template('attendance.html')


@app.route('/data', methods=['POST', 'GET'])
def data():
    startdate = request.form.get('startdate')
    enddate = request.form.get('enddate')
    data = list(mongo.db.attendance.find({"date": {"$gte": (startdate), "$lte": (enddate)}}, {"_id": 0, "name": 1, "date": 1, "time": 1}))
    return render_template("datatable.html", data=data, len=len(data))


@app.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        username = request.form.get('uname')
        password = request.form.get('psw')
        data = list(mongo.db.login.find({'username': username, 'password': password}))
        if(password!='admin@123'):
            return redirect(request.url)
        else:
            return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/home', methods=['POST', 'GET'])
def home():
    return render_template('home.html')

@app.route('/suspect')
def suspect():
    return render_template('suspect_index.html')

@app.route('/suspect_track', methods=['POST', 'GET'])
def suspect_track():
    if 'files' in request.files:
        Date = datetime.now(timezone('Asia/Kolkata')).strftime("%Y-%m-%d")
        files = request.files['files']
        if files and allowed_file(files.filename): 
            filename = secure_filename(files.filename) 
            files.save(os.path.join(app.config['SUSPECT_FOLDER'], filename))
        mongo.save_file(files.filename, files)  
        if(request.form.get('sus_name')==None):
            mongo.db.suspect_details.insert_one({'name': "suspect",'file_name' : files.filename, 'sus_date':Date}) 
        else:
            mongo.db.suspect_details.insert_one({'name': request.form.get('sus_name') ,'file_name' : files.filename, 'sus_date':Date}) 
            mongo.db.attendance.update_one(({'$and': [{'name': request.form.get('sus_name')},{'date': Date}]}),{'$set':{'suspect':'true'}})         
    # return render_template('/find',dash=filename)
    # pattern = filename
    # src_files = os.listdir(original)
    # for file_name in src_files:
    #     if fnmatch.fnmatch(file_name,pattern)==True:
    #         full_file_name= os.path.join(original,file_name)
    #         if os.path.isfile(full_file_name):
    #             shutil.copy(full_file_name,target)
    suspect_name()
    mongo.db.attendance.update_one(({'$and': [{'name': request.form.get('sus_name')},{'date': Date}]}),{'$set':{'suspect':'false'}}) 
    return render_template('video.html')

# @app.route('/video', methods=['POST', 'GET'])
# def video():
#     return render_template('video.html')


if __name__ == '__main__':
    app.run(port=5000, debug=True)

