from flask import Flask, request, render_template, session, make_response, redirect
#from flask import redirect
from functools import wraps
import os
app = Flask(__name__)
app.secret_key = "secretkey"
app.config["UPLOADED_PHOTOS_DEST"] = "static"

books = [
    {
        "id": 1,
        "author": "Hernando de Soto",
        "country": "Peru",
        "language": "English",
        "pages": 209,
        "title": "The Mystery of Capital",
        "year": 1970,
        "price":20.17
    },
    {
        "id": 2,
        "author": "Hans Christian Andersen",
        "country": "Denmark",
        "language": "Danish",
        "pages": 784,
        "title": "Fairy tales",
        "year": 1836,
        "price":35.00
    },
    {
        "id": 3,
        "author": "Dante Alighieri",
        "country": "Italy",
        "language": "Italian",
        "pages": 928,
        "title": "The Divine Comedy",
        "year": 1315,
        "price":16.00
    },
    {
        "id": 4,
        "author": "William Shakespeare",
        "country": "UK",
        "language": "English",
        "pages": 100,
        "title": "Romeo and Juliet",
        "year": 1597,
        "price":60.00
    },
    {
        "id": 5,
        "author": "William Shakespeare",
        "country": "UK",
        "language": "English",
        "pages": 100,
        "title": "Hamlet",
        "year": 1603,
        "price":30.00
    },
    {
        "id": 6,
        "author": "William Shakespeare",
        "country": "UK",
        "language": "English",
        "pages": 100,
        "title": "Macbeth",
        "year": 1623,
        "price":25.90
    },
]

users = [{"username": "testuser", "password": "testuser"}]


def loginrequired(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        # check in session for username
        fromBrowser = session.get("username")
        # check if this is a legitimate user
        for user in users:
            if user["username"] == fromBrowser:
                return fn(*args, **kwargs)
        # otherwise send user to register
        return redirect("static/register.html")

    return decorator


def checkUser(username, password):
    for user in users:
        if username in user["username"] and password in user["password"]:
            return True
    return False


@app.route("/", methods=["GET"])
def firstRoute():
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if checkUser(username, password):
            # set session token to users name
            session["username"] = username
            return render_template(
                "index.html", username=session["username"]
            )
        else:
            return render_template("register.html")
    elif request.method == "GET":
        return render_template("register.html")


@app.route("/logout")
def logout():
    # remove the username from the session if it is there
    session.pop("username", None)
    return "Logged Out of Books"


@app.route("/books", methods=["GET"])
def getBooks():
    try:
        user = session["username"]  
        return render_template("books.html", username=user, books=books)
    except:
        return render_template("register.html")


@app.route("/addbook", methods=["GET", "POST"])
@loginrequired
def addBook():
    username = session["username"]
    if request.method == "GET":
        return render_template("addBook.html")
    if request.method == "POST":
        # expects pure json with quotes everywheree
        author = request.form.get("author")
        title = request.form.get("title")
        newbook = {"author": author, "title": title}
        books.append(newbook)
        return render_template(
            "books.html", books=books, username=username, title="books"
        )
    else:
        return 400


@app.route("/addimage", methods=["GET", "POST"])
@loginrequired
def addimage():
    if request.method == "GET":
        return render_template("addimage.html")
    elif request.method == "POST":
        image = request.files["image"]
        id = request.form.get("number")  # use id to number the image
        imagename = "image" + id + ".png"
        image.save(os.path.join(app.config["UPLOADED_PHOTOS_DEST"], imagename))
        print(image.filename)
        return "image loaded"

    return "all done"

@app.route("/buybook")
def buybook():
    # get the book id parameter passed in the URL:
    try:
        response = "Error - Not overwritten"
        # user = session["username"]
        bookIdParam = request.args.get("bookId")
        booksToPurchase = None
        finalbookList = []
        booksStr = None
        try:
            # input: list
            booksStr = request.cookies.get('booksToPurchase')     
            if(booksStr != None):
                #booksStr = booksToPurchase
                booksList = booksStr.split(',')
                bookListFiltered = []
                booksDict = {}
                for b in booksList:
                    if (b != ''):
                        bookListFiltered.append(b)
                        booksDict[b] = True
                booksDict[bookIdParam] = True
                if(bookIdParam not in bookListFiltered):
                    bookListFiltered.append(bookIdParam)
                for b in books:
                    print(b['id'])
                    if (str(b['id']) in bookListFiltered):
                        finalbookList.append(b)
                booksStr = ''
                for k in booksDict:
                    booksStr += k + ','
                booksToPurchase = booksStr
                print(booksStr)
            else:
                booksStr = bookIdParam + ','
                for b in books:
                    print(b['id'])
                    if (str(b['id']) == bookIdParam):
                        finalbookList.append(b)
                #booksList.append(bookIdParam)
            response = make_response(render_template('buybook.html', booksToPurchase = finalbookList))
            response.set_cookie('booksToPurchase', booksStr)              
        except:
            response = make_response("<h1>Cookie Error (inner)</h1>")
    except:
        response = make_response("<h1>Cookie Error (outer)</h1>")
    return response


# def addCookie(name,contents):
#     response = make_response("<h1>Cookie added!</h1>");
#     response.set_cookie(name, contents)
#     return response


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)
