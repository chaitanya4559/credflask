from flask import Flask, render_template, request, redirect, url_for

from pymongo import MongoClient
from bson.objectid import ObjectId
app=Flask(__name__)
client = MongoClient("mongodb+srv://rsUpkufpWfxZ3AIX:rsUpkufpWfxZ3AIX@cluster0.dll5rqr.mongodb.net/")
db=client["cred"]
users_collection=db["flask_cred"]
students = db["students"]
courses = db["courses"]

authors=db["authors"]
books=db["books"]

@app.before_request
def seed_courses():
    if courses.count_documents({}) == 0:
        courses.insert_many([
            {"name": "Python"},
            {"name": "Flask"},
            {"name": "MongoDB"},
        ])

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
     
@app.route("/add_student",methods=["GET","POST"])
def add_students():
    all_courses=list(courses.find())
    if request.method=="POST":
        name=request.form["name"]
        selected_ids=request.form.getlist("courses")
        course_ids=[ObjectId(cid) for cid in selected_ids]
        students.insert_one({"name": name, "course_ids": course_ids})
        return redirect(url_for("student_details"))

    return render_template("add_student.html", courses=all_courses)  

@app.route("/student_details", methods=["GET"])
def student_details():
    student_list = list(students.find())
    results = []

    for student in student_list:
        enrolled_courses = []
        for cid in student.get("course_ids", []):
            course = courses.find_one({"_id": cid})
            if course:
                enrolled_courses.append(course["name"])
        results.append({
            "name": student["name"],
            "courses": enrolled_courses
        })        
    return render_template("student_details.html", students=results)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        author_name = request.form["author_name"]
        authors.insert_one({"name": author_name,"book_ids": []})
        return redirect(url_for("list_authors"))
    return render_template("add_author.html")
   


@app.route("/authors",methods=["GET","POST"])
def list_authors():
    all_books=list(books.find())
    data=[]
    for author in authors.find():
        author_books=[]
        for book_id in author.get("book_ids",[]):
            book=books.find_one({"_id": book_id})
            if book:
                author_books.append(book["title"])
        data.append({"_id":author["_id"],"name":author["name"],"book_ids":author.get("book_ids",[]),"books":author_books})
    return render_template("authors_list.html",authors=data,books=all_books)             


@app.route("/add_book",methods=["GET","POST"])
def add_book():
    if request.method=="POST":
        title=request.form["title"]
        year=request.form["year"]
        books.insert_one({"title":title,"year":int(year)})
        return redirect(url_for("add_book"))
    return render_template("add_book.html")    


@app.route("/books")
def view_books():
    all_books = []
    for book in books.find():
        book_authors = []
        for aid in book.get("author_ids", []):
            author = authors.find_one({"_id": aid})
            if author:
                book_authors.append(author["name"])
        all_books.append({
            "title": book["title"],
            "year": book["year"],
            "authors": book_authors
        })
    return render_template("books_list.html", books=all_books)




@app.route("/update_author_books/<author_id>", methods=["POST"])
def update_author_books(author_id):
    selected_book_ids = request.form.getlist("books")
    book_object_ids = [ObjectId(bid) for bid in selected_book_ids]
    authors.update_one(
        {"_id": ObjectId(author_id)},
        {"$set": {"book_ids": book_object_ids}}
    )
    books.update_many(
        {"author_ids": ObjectId(author_id)},
        {"$pull": {"author_ids": ObjectId(author_id)}}
    )
    for book_id in book_object_ids:
        books.update_one(
            {"_id": book_id},
            {"$addToSet": {"author_ids": ObjectId(author_id)}}
        )

    return redirect(url_for("list_authors"))


if __name__ == "__main__":
    app.run(debug=True)