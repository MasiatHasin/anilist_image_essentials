from fastapi.responses import Response, RedirectResponse, StreamingResponse
from fastapi import FastAPI, Depends, HTTPException, Request

from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from . import models, crud, schemas, helpers

import bcrypt, requests
from io import BytesIO


models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


# Create Users
@app.post("/user/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.register_user(db=db, user=user)


# Get Users
@app.get("/user/", response_model=list[schemas.UserView])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# Get a User
@app.get("/user/{id}/", response_model=schemas.User)
def read_users(id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


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


# Create Users
@app.post("/activity/", response_model=schemas.Activity)
def create_activity(data: schemas.ActivityCreate, db: Session = Depends(get_db)):
    if crud.activity_exists(db, data.activity_id):
        raise HTTPException(status_code=400, detail="Activity already registered")
    activity = crud.register_activity(db, data)
    if activity is None:
        raise HTTPException(status_code=400, detail="Incorrect Credentials")
    return activity


@app.get("/activity/", response_model=list[schemas.Activity])
def get_activity(
    user: schemas.UserCred,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    activities = crud.get_activities(db, user, skip=skip, limit=limit)
    return activities


# Create Image
@app.post("/image/", response_model=schemas.Image)
def create_activity(data: schemas.ImageCreate, db: Session = Depends(get_db)):
    if crud.image_exists(db, data):
        raise HTTPException(
            status_code=400, detail="Image with this name already exists"
        )
    image = crud.register_image(db, data)
    if image is None:
        raise HTTPException(status_code=400, detail="Incorrect Credentials")
    return image


@app.get("/user/{user_id}/image/{image_name}/{activity_id}")
def get_image(
    user_id: int,
    image_name: str,
    activity_id: int,
    db: Session = Depends(get_db),
):
    # anilist_activity = helpers.get_anilist_activity(activity_id)
    """result = crud.user_activity_exists(db, user_id, activity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Incorrect Information")"""
    image = crud.get_image_by_name(db, user_id, image_name)
    headers = {"User-Agent": "Mozilla/5.0"}
    if not image:
        raise HTTPException(status_code=400, detail="Incorrect Data")
    try:
        response = requests.get(image.url, headers=headers, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Image not found")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error accessing image: {e}")

    # Use StreamingResponse to stream the image data
    return StreamingResponse(
        BytesIO(response.content), media_type=response.headers.get("Content-Type")
    )
