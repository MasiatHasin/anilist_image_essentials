from fastapi.responses import Response, RedirectResponse
from fastapi import FastAPI, Depends, HTTPException, Request

from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from . import models, crud, schemas, helpers

import bcrypt


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


@app.get("/user/{user_id}/image/{image_name}/{activity_id}")
def get_image(
    user_id: int,
    image_name: str,
    activity_id: int,
    db: Session = Depends(get_db),
):
    anilist_activity = helpers.get_anilist_activity(activity_id)
    print(anilist_activity)
    result = crud.user_activity_exists(db, user_id, activity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Incorrect Information")
    image_url = f"https://raw.githubusercontent.com/MasiatHasin/MasiatHasin.github.io/main/{image_name}.jpg"
    return RedirectResponse(image_url)
