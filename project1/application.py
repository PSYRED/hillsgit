import os, uuid,bcrypt,secrets,requests
from flask import Flask, session,request,render_template,redirect,url_for,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from applicatio import *
app = Flask(__name__)
#secret key  'qvUS1KPddUSy3E53MEjvlQ'
# Check for environment variable

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_KEY"]='qvUS1KPddUSy3E53MEjvlQ'
Session(app)

# Set up database
engine = create_engine("postgres://dbiqxvjyhncjwc:c7050534ada23fb8d53a20bc4d47c9638a49eca203a314211f8a6c082ed547bd@ec2-3-230-106-126.compute-1.amazonaws.com:5432/dcgamcbtct7ugl")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def welcome():
    if "username" in session:
        books=db.execute("select * from books limit 20;").fetchall()

        return  render_template("reviews.html",books=books,m=session['username'])
    else:
        return render_template("login.html")


#login section
@app.route('/login',methods=["post","get"])
def login():
    if "username" in session:
        return  redirect(url_for("welcome"))
    if request.method=='POST':
        u,p=request.form.get("username"),request.form.get("password")
        #hashing password
        try:
            hapw=(db.execute("select password from userinfo where username=:username",{"username":u}).first()[0])[2:-1].encode("utf-8")
        except TypeError:
            return render_template("login.html",m="wrong username or password")
        #authenticating user
        check=bcrypt.checkpw(bytes(p.encode("utf-8")),hapw)
        if check== True:
            session['username']=u
            return redirect(url_for("welcome"))
        else:
            return  redirect(request.url)
    return render_template("login.html")

#logout section
@app.route("/logout")
def logout():
    session.pop("username",None)
    return redirect(url_for("welcome"))



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
    return(render_template("auth.html",name=password))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html"),404

@app.route("/book_not_found")
def nobook():
    return render_template("Nobook.html")

"""This is the code for handling user queries of books"""

@app.route("/qbook?", methods=["post","get"])
def queries():
    if "username" in session:

        query=request.form.get("query")
        if query:
            try:
                if db.execute("select * from books where isbn like :isbn",{"isbn":'%'+query+'%'}).fetchall():
                    isbn=db.execute("select * from books where isbn like :isbn",{"isbn":'%'+query+'%'}).fetchall()
                    return render_template("search.html",isbn=isbn)
                elif db.execute("select * from books where title like :title;",{"title":'%'+query+'%'}).fetchall():
                    isbn=db.execute("select * from books where title like :title",{"title":'%'+query+'%'}).fetchall()
                    return render_template("search.html",isbn=isbn)
                elif db.execute("select * from books where author like :author",{"author":'%'+query+'%'}).fetchall():
                    isbn=db.execute("select * from books where author like :author",{"author":'%'+query+'%'}).fetchall()
                    return render_template("search.html",isbn=isbn)
            except TypeError:
                return render_template("error.html")
        return redirect(url_for("nobook"))
    elif "username" not in session:
        return redirect(url_for("welcome"))

"""now you can search for the book using link to the book using its isbn today i'll finish this project starting
   by creating the review page so that it can actually link there for now its linking to the 404 error page cause i haven't created where it links yet.
"""
@app.route("/books/<isbna>",methods=["post","get"])
def booker(isbna):
    if "username" in session:
        if db.execute("select * from books where isbn=:isbn",{"isbn":isbna}).fetchall():
            isbn=db.execute("select * from books where isbn=:isbn",{"isbn":isbna}).fetchall()
            return render_template("search.html",isbn=isbn)
        elif db.execute("select * from books where title=:title",{"title":isbna}).fetchall():
            isbn=db.execute("select * from books where title=:title",{"title":isbna}).fetchall()
            return render_template("search.html",isbn=isbn)
        elif db.execute("select * from books where author=:author",{"author":isbna}).fetchall():
            isbn=db.execute("select * from books where author=:author",{"author":isbna}).fetchall()
            return render_template("search.html",isbn=isbn)

        return redirect(url_for("nobook"))
    elif "username" not in session:
        return redirect(url_for("welcome"))



@app.route("/books/book_detail/<isbna>",methods=["post","get"])
def reviews(isbna):
    #replace isbn and others for revid and it seems here you only need one revid
    if "username" in session:
        goodreadsapi=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"XFmh7WvBEhFzwFOF7GZg","isbns":isbna}).json()["books"][0]["average_rating"]
        rating=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"XFmh7WvBEhFzwFOF7GZg","isbns":"0380795272"}).json()["books"][0]["reviews_count"]
        uid=db.execute("select uid from userinfo where username=:username",{"username":session["username"]}).first()[0]
        bookinfo=db.execute("select * from books where isbn=:isbn",{"isbn":isbna}).fetchall()
        review=db.execute("select username,rating,reviews,bookid from reviews join userinfo on userinfo.uid=reviews.revid where bookid=:bookid",{"bookid":isbna}).fetchall()

        if request.form.get("rev"):
            rev=request.form.get("rev")
            rate=request.form.get("stars")
            revi=db.execute("insert into reviews(revid,rating,reviews,bookid) values(:revid,:rate,:reviews,:bookid);",{"revid":uid,"rate":rate,"reviews":rev,"bookid":isbna})
            db.commit()
        #adding the review
        return render_template("revie.html",isbn=isbna,title=bookinfo[0][1],author=bookinfo[0][2],year=bookinfo[0][3],reviews=review,uid=uid,goodreads=goodreadsapi,rating=rating)

    return redirect(url_for("welcome"))

@app.route("/api/books/<isbna>",methods=["get"])
def api(isbna):
    if db.execute("select isbn from books where isbn=:isbn;",{"isbn":isbna})!=None:
        api= db.execute("select * from books where isbn=:isbn",{"isbn":isbna}).fetchall()
        count=db.execute("select count(*) from reviews where bookid=:bookid",{"bookid":isbna}).first()[0]
        avgscore= requests.get("https://www.goodreads.com/book/review_counts.json", params=({"key":"XFmh7WvBEhFzwFOF7GZg","isbns":isbna})).json()["books"][0]["average_rating"]
    return jsonify(
    {
        "Title":api[0][1],
        "Author":api[0][2],
        "ISBNS":api[0][0],
        "Year":api[0][3],
        "Review count":count,
        "Average score":avgscore

    })
"""A few more corrections on avoiding errors and also the welcome page routing to login page the hard part is over."""
