from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHttpException
from typing import Any

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts : list[dict[str, str|int]] = [
    {
        "id": 1,
        "title": "FastAPI what is it? and why use it",
        "author": "Corey Schafer",
        "content": "This framework is easy to use",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "title": "uv vs pip",
        "author": "Rahul Dev Dahal",
        "content": "Lets compare which is easier to use",
        "date_posted": "May 01, 2025",
    },
]

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )

@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int) -> dict[str, str|int]:
    for post in posts:
        if post.get("id") == post_id:
            return post
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Post not found")
    
@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request:Request, post_id: int) :
    for post in posts:
        if post.get("id") == post_id:
            return templates.TemplateResponse(request, "post.html", {"post": post, "title":post["title"]})
    return templates.TemplateResponse(request, "error.html", {"message": "Not Found!", "status_code":"404"})

@app.exception_handler(StarletteHttpException)
def generate_http_exception_handler(request: Request, exception: StarletteHttpException):
    message = (
        exception.detail
        if exception.detail
        else "An error occured. Please check your request and try again"
    )

    if request.url.path.startswith('/api'):
        return JSONResponse(
            status_code= exception.status_code,
            content={"detail": message}
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code
    )