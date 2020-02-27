import requests,os,csv
from flask import Flask,render_template,request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from flask import jsonify

app=Flask(__name__)
engine=create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))

def main():
    f=open("books.csv")
    reader=csv.reader(f)
    for a,b,c,d in reader:
        print(f"added book with isbn:{a},title:{b},author:{c},year:{d}")
        db.execute(f"insert into books(isbn,title,author,year) values(:isbn,:title,:author,:year)",{"isbn":a,"title":b,"author":c,"year":d})
        db.commit()

with app.app_context():
    if __name__=="__main__":
        main()
