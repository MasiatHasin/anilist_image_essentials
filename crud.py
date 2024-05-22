from sqlalchemy.orm import Session
import models, schemas, math, random
import bcrypt
from sqlalchemy.orm import joinedload


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, username: str):
    return (
        db.query(models.User)
        .options(joinedload(models.User.settings))
        .filter(models.User.username == username)
        .first()
    )


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_image_by_name(name: str, username: str, db: Session):
    user = get_user_by_name(username)
    image = db.query(models.Image).filter(
        models.Image.name == name, models.Image.owner_id == user.id
    )
    return image


def get_hex_color_code(db: Session, username: str, image_type: int):
    user = get_user_by_name(username)
    setting = db.query(models.Setting).filter(models.Setting.owner_id == user.id)
    current_colors = setting.current_colors
    try:
        hex_color_code = current_colors[image_type]
    except:
        if image_type <= (len(current_colors) - 1) - image_type:
            rand_type = random.randint(0, image_type)
        else:
            rand_type = random.randint(image_type, len(current_colors) - 1)
        hex_color_code = current_colors[rand_type]
    return hex_color_code


def check_user_cred(data: schemas.ExtractColors, db: Session):
    user = (
        db.query(models.User)
        .filter(
            models.User.username == data.username,
            models.User.password == data.password,
        )
        .first()
    )
    if user is not None:
        return True
    return False


def save_colors(data: schemas.ExtractColors, result: str, db: Session):
    if not check_user_cred(data, db):
        return False
    user = get_user_by_name(db, data.username)
    user_setting = (
        db.query(models.Setting).filter(models.Setting.owner_id == user.id).first()
    )
    user_setting.current_colors = result
    db.commit()
    return True
