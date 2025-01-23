from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
# Load .env file
load_dotenv()
app = FastAPI()

# Database setup
# DATABASE_URL = "sqlite:///./blogg.db"


DATABASE_URL = os.getenv('DATABASE_URL')
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Templates setup
templates = Jinja2Templates(directory="templates")

# Blog model
class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    title = Column(String, index=True)
    content = Column(String)

Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def read_blogs(request: Request):
    
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def read_blogs(request: Request):
    
    return templates.TemplateResponse("about.html", {"request": request})

# @app.get("/blogs", response_class=HTMLResponse)
# def read_blogs(request: Request):
#     db = SessionLocal()
#     blogs = db.query(Blog).all()
#     db.close()
#     return templates.TemplateResponse("blogs.html", {"request": request, "blogs": blogs})




@app.get("/blogs", response_class=HTMLResponse)
def read_blogs(request: Request):
    db = SessionLocal()
    blogs = db.query(Blog).all()
    db.close()

    # Truncate content to the first 30 words for each blog
    truncated_blogs = [
        {
            "id": blog.id,
            "title": blog.title,
            "username": blog.username,
            "content": " ".join(blog.content.split()[:30]) + "..." if len(blog.content.split()) > 30 else blog.content
        }
        for blog in blogs
    ]

    return templates.TemplateResponse("blogs.html", {"request": request, "blogs": truncated_blogs})



@app.get("/create", response_class=HTMLResponse)
def create_blog_form(request: Request):
    return templates.TemplateResponse("create_blog.html", {"request": request})

@app.post("/create", response_class=HTMLResponse)
def create_blog(username: str = Form(...), title: str = Form(...), content: str = Form(...)):
    db = SessionLocal()
    new_blog = Blog(username=username, title=title, content=content)
    db.add(new_blog)
    db.commit()
    db.close()
    return RedirectResponse(url="/blogs", status_code=303)


@app.get("/blog/{blog_id}", response_class=HTMLResponse)
def get_blog(blog_id: int, request: Request):
    db = SessionLocal()
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    db.close()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return templates.TemplateResponse("blog.html", {"request": request, "blog": blog})