from typing import Optional
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import datetime as _dt
import passlib.hash as _hash

import database as _database


class User(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.INTEGER, primary_key=True, index=True)
    name = _sql.Column(_sql.String)
    email = _sql.Column(_sql.String, unique=True)
    email_verified_at = _sql.Column(_sql.DateTime, nullable=True)
    password = _sql.Column(_sql.String)
    remember_me = _sql.Column(_sql.BOOLEAN, default=False)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    updated_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.password)

    surveys = _orm.relationship("Survey", back_populates="user")


class Survey(_database.Base):
    __tablename__ = "surveys"
    id = _sql.Column(_sql.INTEGER, primary_key=True, index=True)
    title = _sql.Column(_sql.String)
    slug = _sql.Column(_sql.String)
    image = _sql.Column(_sql.String, nullable=True)
    description = _sql.Column(_sql.Text, nullable=True)
    status = _sql.Column(_sql.SMALLINT)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    updated_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    expire_date = _sql.Column(_sql.DateTime, nullable=True)
    user_id = _sql.Column(_sql.INTEGER, _sql.ForeignKey("users.id"))

    user = _orm.relationship("User", back_populates="surveys")
    questions = _orm.relationship("SurveyQuestion", back_populates="survey")
    answers = _orm.relationship("SurveyAnswer", back_populates="survey")


class SurveyQuestion(_database.Base):
    __tablename__ = "survey_questions"
    id = _sql.Column(_sql.INTEGER, primary_key=True, index=True)
    type = _sql.Column(_sql.String)
    question = _sql.Column(_sql.String)
    description = _sql.Column(_sql.Text, nullable=True)
    data = _sql.Column(_sql.Text, nullable=True)
    created_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    updated_at = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    survey_id = _sql.Column(_sql.INTEGER, _sql.ForeignKey("surveys.id"))

    survey = _orm.relationship("Survey", back_populates="questions")


class SurveyAnswer(_database.Base):
    __tablename__ = "survey_answers"
    id = _sql.Column(_sql.INTEGER, primary_key=True, index=True)
    start_date = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    end_date = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    survey_id = _sql.Column(_sql.INTEGER, _sql.ForeignKey("surveys.id"))

    survey = _orm.relationship("Survey", back_populates="answers")


class SurveyQuestionAnswer(_database.Base):
    __tablename__ = "survey_question_answers"
    id = _sql.Column(_sql.INTEGER, primary_key=True, index=True)
    text = _sql.Column(_sql.String)
    survey_question_id = _sql.Column(
        _sql.INTEGER, _sql.ForeignKey("survey_questions.id"))
    survey_answer_id = _sql.Column(
        _sql.INTEGER, _sql.ForeignKey("survey_answers.id"))

    survey_question = _orm.relationship("SurveyQuestion")
    survey_answer = _orm.relationship("SurveyAnswer")
