from sqlalchemy.orm import Session
from . import models, schemas
import math, random
import bcrypt


def db_save(db: Session, db_instance):
    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_activities(
    db: Session, user: schemas.UserCred, skip: int = 0, limit: int = 100
):
    user = validate_data(db, user)
    return (
        db.query(models.Activity)
        .filter(models.Activity.owner_id == user.id)
        .offset(skip)
        .limit(limit)
    )


def register_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username, password=user.password, anilist_name=user.anilist_name
    )
    db_save(db, db_user)
    db_setting = models.Setting(owner_id=db_user.id)
    db_save(db, db_setting)
    return db_user


def activity_exists(db: Session, activity_id: int):
    return (
        db.query(models.Activity)
        .filter(models.Activity.activity_id == activity_id)
        .first()
    )


def validate_data(db: Session, data: schemas.ActivityCreate):
    return (
        db.query(models.User)
        .filter(
            models.User.password == data.password, models.User.username == data.username
        )
        .first()
    )


def register_activity(db: Session, data: schemas.ActivityCreate):
    user = validate_data(db, data.user)
    if not user:
        return None
    db_activity = models.Activity(owner_id=user.id, activity_id=data.activity_id)
    db_save(db, db_activity)
    return db_activity


def user_activity_exists(db, user_id, activity_id):
    return db.query(models.Activity).filter(models.Activity.owner_id == user_id)
