import csv
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_books():
    with open("books.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))

@app.get("/")
def index(request: Request):
    books = get_books()

    ua_books = [b for b in books if b["language"] == "ua"]
    en_books = [b for b in books if b["language"] == "en"]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "ua_books": ua_books,
            "en_books": en_books
        }
    )

@app.get("/books/new")
def new_book_form(request: Request):
    return templates.TemplateResponse(
        "new_book.html",
        {"request": request}
    )
    
@app.get("/books/{book_id}")
def book_page(request: Request, book_id: int):
    books = get_books()
    book = next((b for b in books if int(b["id"]) == book_id), None)

    return templates.TemplateResponse(
        "object.html",
        {
            "request": request,
            "book": book
        }
    )

@app.post("/books/new")
def create_book(
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    pages: int = Form(...),
    image: str = Form(...),
    language: str = Form(...)
):

    books = get_books()

    new_id = max(int(b["id"]) for b in books) + 1 if books else 1

    new_book = {
        "id": new_id,
        "title": title,
        "author": author,
        "year": year,
        "pages": pages,
        "image": image,
        "language": language
    }

    books.append(new_book)

    with open("books.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_book.keys())
        writer.writeheader()
        writer.writerows(books)

    return RedirectResponse(url="/", status_code=303)

@app.get("/info")
def info(request: Request):
    return templates.TemplateResponse(
        "info.html",
        {"request": request}
    )