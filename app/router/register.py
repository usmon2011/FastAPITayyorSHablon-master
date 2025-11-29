from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from app.model import db, User
from app.schemes import UserCreate
from app.send_from_gmail import send_gmail
import random

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIRECTION = "app/media"


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html",
                                      {"request": request})


@router.post("/register")
async def create_register(request: Request):
    form = await request.form()

    gmail = form.get("gmail")
    password = form.get("password")
    confirm_password = form.get("confirm_password")
    message = str(random.randint(111_111, 999_999))

    try:
        data = UserCreate(
            gmail=gmail,
            password=password,
            confirm_password=confirm_password)
    except ValidationError as e:
        error_message = e.errors()[0]["msg"]
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": error_message
        })

    user = User(
        gmail=data.gmail,
        password=data.password,
        confirm_password=data.confirm_password,
        generate_code=message
    )
    db.add(user)
    db.commit()

    print(send_gmail(gmail_user="shohruh.abd2223@gmail.com",
                     recipient_email=user.gmail,
                     message=message))


    return RedirectResponse("/check-gmail", status_code=HTTP_302_FOUND)

#  login --------------------------------------------------------------
@router.get("/login.html", response_class=HTMLResponse)
async def form_login(request: Request):
    return templates.TemplateResponse("login.html",
                                      {"request": request})


@router.post("/login")
async def login_user(request: Request):
    form = await request.form()
    gmail = form.get("gmail")
    password = form.get("password")

    user = db.query(User).filter(User.gmail==gmail).first()

    if not user or user.password != password:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email yoki parol noto‘g‘ri"
        })

    if user.is_active == False:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Tasdiqlash kodi xato"
        })

    response = RedirectResponse("/", status_code=HTTP_302_FOUND)
    return response

# -------------------------------------------------------

@router.get("/check-gmail", response_class=HTMLResponse)
async def form_gmail(request: Request):
    return templates.TemplateResponse("check_gmail.html",
                                      {"request": request})


@router.post("/check-gmail")
async def check_user(request: Request):
    form = await request.form()
    generate_code = form.get("generate_code")

    user = db.query(User).filter(User.generate_code==generate_code).first()
    if user:
        user.is_active = True
        db.commit()
    else:
        return templates.TemplateResponse("check_gmail.html", {
            "request": request,
            "error": "Tasdiqlash kodi noto'g'ri"
        })

    return RedirectResponse("/login.html", status_code=HTTP_302_FOUND)
