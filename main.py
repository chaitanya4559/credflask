from flask import Flask, render_template, request, redirect, url_for

from pymongo import MongoClient
from bson.objectid import ObjectId
app=Flask(__name__)
client = MongoClient("mongodb+srv://rsUpkufpWfxZ3AIX:rsUpkufpWfxZ3AIX@cluster0.dll5rqr.mongodb.net/")
db=client["cred"]
users_collection=db["flask_cred"]
@app.route("/")
def index():
    users=list(users_collection.find())
    return render_template("user.html",users=users)
@app.route("/add",methods=["GET","POST"])
def add_user():
    if request.method=="POST":
        name=request.form["name"]
        email=request.form["email"]
        users_collection.insert_one({"name":name,"email":email})
        return redirect(url_for("index"))
    return render_template("add_user.html")    
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_user(id):
    user = users_collection.find_one({"_id": ObjectId(id)})      
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        users_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": name, "email": email}})
        return redirect(url_for("index"))
    return render_template("edit_user.html", user=user)
@app.route("/delete/<id>")
def delete_user(id):
    users_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))  
if __name__ == "__main__":
    app.run(debug=True)         