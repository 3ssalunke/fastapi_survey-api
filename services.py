import sqlalchemy.orm as _orm
import passlib.hash as _hash
import jwt as _jwt
import fastapi as _fastapi
import datetime as _dt
import slugify as _slugify
import json as _json

import database as _database
import schemas as _schemas
import models as _models
import utils as _utils

JWT_SECRET = "ryorfboweoebewhweeu832"


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()


def create_user(user: _schemas.UserCreate, db: _orm.session):
    user_obj = _models.User(name=user.name, email=user.email,
                            password=_hash.bcrypt.hash(user.password), remember_me=user.remember_me)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return _schemas.User.from_orm(user_obj)


def authenticate_user(email: str, password: str, db: _orm.Session):
    user = get_user_by_email(email, db)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


def create_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)
    user_dict = {"id": user_obj.id,
                 "name": user_obj.name, "email": user_obj.email}

    return _jwt.encode(user_dict, JWT_SECRET)


def get_user_from_token(request: _fastapi.Request,  db: _orm.Session):
    if request.headers.get("authorization") is None:
        raise _fastapi.HTTPException(
            status_code=401, detail="Authorization token missing")
    elif request.headers.get("authorization").split(" ")[0] != "Bearer":
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid token")

    token = request.headers.get(
        "authorization").split(" ")[1]
    payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    user = db.query(_models.User).filter(
        _models.User.email == payload["email"]).first()
    if not user:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Token")
    return user


def create_survey(survey: _schemas.SurveyCreate, user_id: int, db: _orm.session):
    slug = _slugify.slugify(survey.title)
    image_path = _utils.save_image(survey.image, slug)
    expire_date = _dt.datetime.strptime(
        survey.expire_date, '%Y-%m-%d')

    survey_obj = _models.Survey(title=survey.title, slug=slug, image=image_path,
                                description=survey.description, status=survey.status, expire_date=expire_date, user_id=user_id)
    db.add(survey_obj)
    db.commit()
    db.refresh(survey_obj)

    if len(survey.questions) != 0:
        for question in survey.questions:
            question_obj = _models.SurveyQuestion(type=question.type, question=question.question,
                                                  description=question.description, data=_json.dumps(question.data), survey_id=survey_obj.id)
            db.add(question_obj)
            db.commit()

    return _schemas.Survey.from_orm(survey_obj)


def get_survey(survey_id: int, user_id: int, db: _orm.session):
    survey_obj = db.query(_models.Survey).filter(
        _models.Survey.id == survey_id).first()

    if not survey_obj.user.id == user_id:
        raise _fastapi.HTTPException(
            status_code=403, detail="You are not authorized to access this survey")

    return _schemas.Survey.from_orm(survey_obj)


def get_surveys(user_id: int, db: _orm.session):
    surveys_list = db.query(_models.Survey).filter(
        _models.Survey.user_id == user_id).all()

    return list(map(_schemas.Survey.from_orm, surveys_list))


def update_survey(survey: _schemas.SurveyUpdate, user_id: int, db: _orm.session):
    survey_obj = db.query(_models.Survey).filter(
        _models.Survey.id == survey.id).first()

    if survey_obj is None:
        raise _fastapi.HTTPException(
            status_code=400, detail="survey does not exist")

    if not survey_obj.user.id == user_id:
        raise _fastapi.HTTPException(
            status_code=403, detail="You are not authorized to access this survey")

    try:
        if survey_obj.image != "no_image":
            _utils.delete_image(survey_obj.image)
    except:
        raise _fastapi.HTTPException(
            status_code=500, detail="Internal image handling error")

    slug = _slugify.slugify(survey.title)
    image_path = _utils.save_image(survey.image, slug)

    survey_obj.title = survey.title
    survey_obj.slug = slug
    survey_obj.description = survey.description
    survey_obj.image = image_path
    survey_obj.status = survey.status
    survey_obj.expire_date = _dt.datetime.strptime(
        survey.expire_date, '%Y-%m-%d')
    survey_obj.updated_at = _dt.datetime.now()

    db.add(survey_obj)
    db.commit()
    db.refresh(survey_obj)

    return _schemas.Survey.from_orm(survey_obj)


def delete_survey(survey_id: int, user_id: int, db: _orm.session):
    survey_obj = db.query(_models.Survey).filter(
        _models.Survey.id == survey_id).first()

    if survey_obj is None:
        raise _fastapi.HTTPException(
            status_code=400, detail="survey does not exist")

    if not survey_obj.user.id == user_id:
        raise _fastapi.HTTPException(
            status_code=403, detail="You are not authorized to access this survey")

    try:
        if survey_obj.image != "no_image":
            _utils.delete_image(survey_obj.image)
    except:
        raise _fastapi.HTTPException(
            status_code=500, detail="Internal image handling error")

    db.delete(survey_obj)
    db.commit()
    return
