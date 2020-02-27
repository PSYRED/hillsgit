import os, uuid,bcrypt,secrets
from flask import Flask, session,request,render_template,redirect,url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from applicatio import *
app = Flask(__name__)
#secret key  'qvUS1KPddUSy3E53MEjvlQ'
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_KEY"]='qvUS1KPddUSy3E53MEjvlQ'
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def welcome():
    return render_template("login.html")


#login section
@app.route('/login',methods=["post","get"])
def login():
    if request.method=='POST':
        u,p=request.form.get("username"),request.form.get("password")
        #hashing password
        hapw=(db.execute("select password from userinfo where username=:username",{"username":u}).first()[0])[2:-1].encode("utf-8")
        #authenticating user
        chec=bcrypt.checkpw(bytes(p.encode("utf-8")),hapw)
        if chec== True:
            session['user']=u
            return render_template("reviews.html",m=session['user'])
        else:
            return  redirect(request.url)
    return redirect(url_for("welcome"),m="wrong")




#signup section



@app.route("/signup")
def signup():
    return render_template("signup.html")
@app.route("/signup/welcome",methods=["post"])
def new():
    r=uuid.uuid4()
    sal=bcrypt.gensalt()
    pw=request.form.get("password")
    password=bcrypt.hashpw(bytes(pw,"utf-8"),sal)
    password,sal=str(password),str(sal)
    firstname,lastname,email,username= request.form.get("first_name"),request.form.get("last_name"),request.form.get("email"),request.form.get("username")
    db.execute("insert into userp(uui,first_name,last_name,email) values(:uui,:firstname,:lastname,:email)",{"uui":r,"firstname":firstname,"lastname":lastname,"email":email})
    db.execute("insert into userinfo(uuid,username,salty,password) values(:uuid,:username,:salty,:password)",{"uuid":r,"username":username,"salty":sal,"password":password})
    db.commit()
    return(render_template("welcome.html",name=password))
