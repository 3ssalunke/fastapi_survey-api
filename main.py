import fastapi as _fastapi
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_200_OK
from fastapi.staticfiles import StaticFiles
import sqlalchemy.orm as _orm

import services as _services
import schemas as _schemas

app = _fastapi.FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=['http://localhost:3000'],
                   allow_methods=['*'],
                   allow_headers=['*']
                   )


app.mount(
    "/static/images", StaticFiles(directory="images"), name="static")


@app.get("/api/status", status_code=HTTP_200_OK)
async def status():
    return {'message': "server is up"}


@app.post("/api/auth/register")
async def create_user(user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(
            status_code=400, detail="Email already in use")

    _user = _services.create_user(user, db)
    _token = _services.create_token(_user)
    _user = {"id": _user.id, "name": _user.name, "email": _user.email}
    return dict(user=_user, token=_token, token_type="bearer")


@app.post("/api/auth/login")
async def login_user(user: _schemas.UserLogin, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    authenticated_user = _services.authenticate_user(
        user.email, user.password, db)

    if not authenticated_user:
        raise _fastapi.HTTPException(
            status_code=400, detail="wrong credentials")

    _token = _services.create_token(authenticated_user)
    return dict(token=_token, token_type="bearer")


@app.get("/api/auth/logout")
async def logout_user(request: _fastapi.Request, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = _services.get_user_from_token(request, db)
    return {"message": "success"}


@app.post("/api/survey")
async def create_survey(survey: _schemas.SurveyCreate, request: _fastapi.Request, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = _services.get_user_from_token(request, db)
    survey = _services.create_survey(survey, user.id, db)
    return {"survey": survey.dict()}


@app.get("/api/survey/{survey_id}")
async def get_survey(survey_id: int, request: _fastapi.Request, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = _services.get_user_from_token(request, db)
    survey = _services.get_survey(survey_id, user.id, db)
    return {"survey": survey.dict()}


@app.get("/api/survey")
async def get_surveys(request: _fastapi.Request, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = _services.get_user_from_token(request, db)
    surveys = list(map(lambda x: x.dict(), _services.get_surveys(user.id, db)))

    return {"surveys": surveys}


@app.put("/api/survey")
async def update_survey(survey: _schemas.SurveyUpdate, request: _fastapi.Request, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = _services.get_user_from_token(request, db)
    survey = _services.update_survey(survey, user.id, db)
    return {"survey": survey.dict()}


@app.delete("/api/survey/{survey_id}")
async def delete_survey(survey_id: int, request: _fastapi.Request, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = _services.get_user_from_token(request, db)
    survey = _services.delete_survey(survey_id, user.id, db)
    return {"message": "success"}
