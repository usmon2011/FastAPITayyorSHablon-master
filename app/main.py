import random
import shutil

from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from fastapi import FastAPI, Request, UploadFile, Depends
from fastapi.responses import HTMLResponse
from starlette.status import HTTP_302_FOUND

from app.bot import CHAT_ID, bot
from app.model import User, db, Contact, Product
from app.schemes import UserCreate
from app.send_from_gmail import send_gmail
import os

from app.model import SessionLocal, get_db

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory='app/static'), name="static")



@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/index.html", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about.html", response_class=HTMLResponse)
def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/contact.html", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html",
                                      {"request": request})


@app.post("/contact.html")
async def create_register(request: Request):
    form = await request.form()

    name = form.get("name")
    email = form.get("email")
    subject = form.get("subject")
    text = form.get("text")

    contact = Contact(
        name=name,
        email=email,
        subject=subject,
        text=text)
    db.add(contact)
    db.commit()

    text = f"""<b>ism:</b> {name}
<b>email:</b>{email}
<b>subject:</b> {subject}
<b>Text:</b> {text}"""
    await bot.send_message(chat_id=CHAT_ID,
                           text=text,
                           parse_mode="HTML")

    return RedirectResponse("/index.html", status_code=HTTP_302_FOUND)


@app.get("/services.html", response_class=HTMLResponse)
def read_services(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})


@app.get("/properties.html", response_class=HTMLResponse)
async def shop_func(request: Request, page: int = 1, db: Session = Depends(get_db)):
    per_page = 6
    offset_value = (page - 1) * per_page
    products = db.query(Product).offset(offset_value).limit(per_page).all()
    total = db.query(Product).count()
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse("properties.html", {
        "request": request,
        "products": products,
        "page": page,
        "total_pages": total_pages
    })
@app.get("/property-single.html", response_class=HTMLResponse)
async def property(request: Request):
    return templates.TemplateResponse("property-single.html",
                                      {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html",
                                      {"request": request})



@app.post("/register")
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
@app.get("/login", response_class=HTMLResponse)
async def form_login(request: Request):
    return templates.TemplateResponse("login.html",
                                      {"request": request})


@app.post("/login")
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



@app.get("/check-gmail", response_class=HTMLResponse)
async def form_gmail(request: Request):
    return templates.TemplateResponse("check_gmail.html",
                                      {"request": request})


@app.post("/check-gmail")
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

    return RedirectResponse("/login", status_code=HTTP_302_FOUND)
#------------------------------------------------------------------------
@app.get("/create-product", response_class=HTMLResponse)
async def form_category(request: Request):
    return templates.TemplateResponse("create-product.html",
                                      {"request": request})


@app.post("/create-product")
async def create_product(request: Request):
    form = await request.form()

    category = str(form.get("category"))
    price = float(form.get("price"))
    address = str(form.get("address"))

    image: UploadFile = form.get("image")
    file_path = os.path.join(templates, image.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    product = Product(image=image.filename,
                      price=price,
                      address=address,
                      category=category)
    db = SessionLocal()
    db.add(product)
    db.commit()
    db.close()

    return RedirectResponse("/index.html", status_code=HTTP_302_FOUND)