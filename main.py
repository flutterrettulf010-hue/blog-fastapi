from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHttpException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Any
from schemas import PostCreate, PostResponse

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

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request:Request, post_id: int) :
    for post in posts:
        if post.get("id") == post_id:
            return templates.TemplateResponse(request, "post.html", {"post": post, "title":post["title"]})
    return templates.TemplateResponse(request, "error.html", {"message": "Not Found!", "status_code":"404"})

# setting response_model is very important, as it removes any extra info that is not
# in PostResponse and if there is any missing required fields in PostResponse it will throw error
# helping us
# 
# response_model also help to show correct schema in Swagger
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int) -> dict[str, str|int]:
    for post in posts:
        if post.get("id") == post_id:
            return post
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Post not found")

@app.post("/api/post", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
# fastapi understands this typehint and automatically parses the json body
# and validates it against schema and returns 422 validation error with whats missing
# if everything is correct, runs fun
def create_post(post: PostCreate):
    # list comprehension
    # new_id = max((p["id"] for p in posts), default=0) + 1
    # temp code will see what is the max post id currently and adds 1 to it
    # to generate new post id
    new_id = 1
    for p in posts:
        if new_id < p["id"]:
            new_id = p["id"]
    new_id+=1

    new_post: PostResponse = PostResponse(**{
        "id": new_id,
        "title": post.title,
        "author": post.author,
        "content": post.content,
        "date_posted": "April 19, 2025",
    })

    posts.append(new_post.model_dump_json())
    print(posts)
    return new_post




# catch http error
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

# catch request validation error and instead of using exception.status we directly use 422
@app.exception_handler(RequestValidationError)
def general_http_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith('/api'):
        return JSONResponse(content= {"detail": exception.errors()}, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code" : status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again",
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
        },
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


