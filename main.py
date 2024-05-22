from fastapi.responses import StreamingResponse, Response
from helpers import (
    extract_colors_helper,
    generate_image_helper,
)
from fastapi import FastAPI, Depends, HTTPException

from database import SessionLocal, engine
from sqlalchemy.orm import Session
import models, crud, schemas

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/generate-image")
def generate_image(name: str, username: str, db: Session = Depends(get_db)):
    image = crud.get_image_by_name(name, username, db)
    hex_color = crud.get_hex_color_code(username, db, image.type)
    retry_count = 5
    result = None
    while result is None and retry_count > 0:
        result = generate_image_helper(name)
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


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.UserView])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{username}/", response_model=schemas.User)
def read_users(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_name(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
