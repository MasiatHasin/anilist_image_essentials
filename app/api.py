from fastapi.responses import Response, RedirectResponse
from fastapi import FastAPI, Depends, HTTPException, Request

from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from . import models, crud, schemas

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


[
    (b"connection", b"close"),
    (b"x-forwarded-for", b"114.130.184.79,::ffff:10.10.11.55,::ffff:10.10.87.49"),
    (b"x-forwarded-proto", b"https,http,http"),
    (b"x-forwarded-port", b"443,80,80"),
    (b"host", b"anilist-essentials.glitch.me"),
    (
        b"user-agent",
        b"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    ),
    (
        b"accept",
        b"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    ),
    (b"accept-language", b"en-US,en;q=0.5"),
    (b"accept-encoding", b"gzip, deflate, br, zstd"),
    (b"referer", b"https://glitch.com/"),
    (b"upgrade-insecure-requests", b"1"),
    (b"sec-fetch-dest", b"iframe"),
    (b"sec-fetch-mode", b"navigate"),
    (b"sec-fetch-site", b"cross-site"),
    (b"priority", b"u=4"),
    (b"pragma", b"no-cache"),
    (b"cache-control", b"no-cache"),
    (b"x-forwarded-host", b"anilist-essentials.glitch.me"),
    (b"traceparent", b"00-7bfbec9fb2964267b5cbeb0c87bdd782-e71c5841cee04a62-01"),
]


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


@app.get("/user/{user_id}/image/{image_name}/{activity_id_hash}")
def get_image(
    user_id: int,
    image_name: str,
    activity_id: int,
    db: Session = Depends(get_db),
):
    result = crud.user_activity_exists(db, user_id, activity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Incorrect Information")
    image_url = f"https://raw.githubusercontent.com/MasiatHasin/MasiatHasin.github.io/main/{image_name}.jpg"
    return RedirectResponse(image_url)
