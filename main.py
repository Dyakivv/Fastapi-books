import csv
from abc import ABC, abstractmethod
from typing import List, Optional
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Book:
    def __init__(self, id: int, title: str, author: str, year: int, pages: int, image: str, language: str):
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self.pages = pages
        self.image = image  
        self.language = language

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "pages": self.pages,
            "image": self.image,
            "language": self.language
        }

class BaseRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Book]:
        pass

    @abstractmethod
    def get_by_id(self, obj_id: int) -> Optional[Book]:
        pass

    @abstractmethod
    def add(self, obj: Book) -> None:
        pass

class CSVBookRepository(BaseRepository):
    _instance = None
    _filename = "books.csv"
    _fieldnames = ["id", "title", "author", "year", "pages", "image", "language"]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_all(self) -> List[Book]:
        books = []
        try:
            with open(self._filename, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    books.append(Book(
                        id=int(row["id"]),
                        title=row["title"],
                        author=row["author"],
                        year=int(row["year"]),
                        pages=int(row["pages"]),
                        image=row["image"],
                        language=row["language"]
                    ))
        except FileNotFoundError:
            return []
        return books

    def get_by_id(self, obj_id: int) -> Optional[Book]:
        books = self.get_all()
        return next((b for b in books if b.id == obj_id), None)

    def add(self, obj: Book) -> None:
        books = self.get_all()
        books.append(obj)
        
        with open(self._filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self._fieldnames)
            writer.writeheader()
            for b in books:
                writer.writerow(b.to_dict())

repo = CSVBookRepository()

@app.get("/")
def index(request: Request):
    books = repo.get_all()

    ua_books = [b for b in books if b.language == "ua"]
    en_books = [b for b in books if b.language == "en"]

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
    book = repo.get_by_id(book_id)

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
    books = repo.get_all()
    new_id = max(b.id for b in books) + 1 if books else 1
    
    new_book = Book(
        id=new_id,
        title=title,
        author=author,
        year=year,
        pages=pages,
        image=image,
        language=language
    )

    repo.add(new_book)

    return RedirectResponse(url="/", status_code=303)

@app.get("/info")
def info(request: Request):
    return templates.TemplateResponse(
        "info.html",
        {"request": request}
    )