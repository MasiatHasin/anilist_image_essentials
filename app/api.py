from fastapi.responses import StreamingResponse, Response
from .helpers import (
    extract_colors_helper,
    generate_image_helper,
)
from fastapi import FastAPI, Depends, HTTPException

from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from . import models, crud, schemas

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/generate-image/")
def generate_image(name: str, username: str, db: Session = Depends(get_db)):
    image = crud.get_image_by_name(name, username, db)
    if not image:
        return HTTPException(
            detail="Image not found. Are you sure you registered the image?",
            status_code=404,
        )
    hex_color = crud.get_hex_color_code(db, username, image.type)
    retry_count = 5
    result = None
    while result is None and retry_count > 0:
        result = generate_image_helper(image.url, hex_color)
        retry_count -= 1
        print("retrying")

    return StreamingResponse(result, media_type="image/png")


@app.post("/extract-colors/")
def extract_colors(
    data: schemas.ExtractColors,
    db: Session = Depends(get_db),
):
    if not crud.check_user_cred(data, db):
        return HTTPException(detail="Unauthorized", status_code=401)
    retry_count = 5
    result = None
    while result is None and retry_count > 0:
        result = extract_colors_helper(data.image_url, data.num_colors)
        retry_count -= 1
        print("retrying")
    if not crud.save_colors(data, result, db):
        return HTTPException(detail="An error occured", status_code=500)
    return Response(content=result, status_code=200)


# Create Users
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.register_user(db=db, user=user)


# Get Users
@app.get("/users/", response_model=list[schemas.UserView])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# Get a User
@app.get("/users/{username}/", response_model=schemas.User)
def read_users(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_name(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Post Images
@app.post("/image/")
def post_image(image: schemas.ImageCreate, db: Session = Depends(get_db)):
    try:
        user = crud.get_user_by_name(db, image.username)
        image = crud.post_image(db, image, user.id)
        return image
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="User not found")


# Root Info
@app.get("/", tags=["Root"])
def root():
    return Response(
        content="""<html>
                     <body>
                       <p>Welcome to the Anilist Essentials API by Mashiat.</p>
                       <p>Go to <a href='/docs/'>/docs/</a> for documentation.</p>
                     </body>
                   </html>"""
    )
