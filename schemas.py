import datetime as _dt
import pydantic as _pydantic
import typing as _typing


class _UserBase(_pydantic.BaseModel):
    email: str


class UserLogin(_UserBase):
    password: str

    class Config:
        orm_mode = True


class UserCreate(_UserBase):
    name: str
    password: str
    remember_me: bool

    class Config:
        orm_mode = True


class User(_UserBase):
    id: int
    name: str
    remember_me: bool
    email_verified_at: _dt.datetime | None
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        orm_mode = True


class _QuestionBase(_pydantic.BaseModel):
    type: str
    question: str
    description: str
    data: _typing.Any


class QuestionCreate(_QuestionBase):
    class Config:
        orm_mode = True


class QuestionUpdate(_QuestionBase):
    id: int
    survey_id: int

    class Config:
        orm_mode = True


class Question(_QuestionBase):
    id: int
    survey_id: int
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        orm_mode = True


class _SurveyBase(_pydantic.BaseModel):
    title: str
    image: str
    description: str
    status: int
    expire_date: _dt.datetime


class SurveyCreate(_SurveyBase):
    expire_date: str
    questions: _typing.List[QuestionCreate]

    class Config:
        orm_mode = True


class SurveyUpdate(_SurveyBase):
    id: int
    expire_date: str
    questions: _typing.List[QuestionUpdate]

    class Config:
        orm_mode = True


class Survey(_SurveyBase):
    id: int
    slug: str
    user_id: int
    questions: _typing.List[Question]
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        orm_mode = True
