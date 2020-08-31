import os
import sys
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()
 
class User(Base):
    __tablename__ ="User"
    user_name = Column(String(30), primary_key = True)
    e_mail = Column(String(30), nullable = False)
    name = Column(String(32), index = True)
    password_hash = Column(String(64))

    def hash_password(self,password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self,password):
        return pwd_context.verify(password,self.password_hash)
 
class Blog(Base):
    __tablename__ = 'Blog'

    blog_id = Column(Integer, primary_key = True, autoincrement = True)
    author = Column(String(30),ForeignKey('User.user_name'))
    title = Column(String(30),nullable=False)
    body = Column(String(40))
    description = Column(String(250),nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    link = Column(String(50))
    image = Column(String(100))

#We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
       return {
           'blog_id':self.blog_id,
           'author':self.author,
           'title':self.title,
           'body':self.body,
           'description':self.description,
           'date_created':self.date_created,
           'link':self.link,
           'image':self.image
       }
 
class Comment(Base):
    __tablename__ = 'Comment'

    comment_id = Column(Integer, primary_key = True, autoincrement = True)
    blog_id = Column(Integer, ForeignKey('Blog.blog_id'))
    author = Column(String(30),ForeignKey('User.user_name'))
    body = Column(String(40))
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
#We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
       return {
           'id' : self.comment_id,
           'blog_id':self.blog_id,
           'author' : self.author,
           'body': self.body,
           'date_created' : self.date_created,
       }

class Audit(Base):
    __tablename__ ="Audit"
    audit_id = Column(Integer, primary_key = True, autoincrement = True)
    user_name = Column(String(30), ForeignKey('User.user_name'))
    activity = Column(String(30),nullable = False)
    which_activity = Column(String(30),nullable = True)
    time = Column(DateTime, nullable=False, default = datetime.utcnow)
    activity_data = Column(Text, nullable = True )

#We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
       return {
           'id':self.audit_id,
           'user_id':self.user_name,
           'activity':self.activity,
           'which_activity':self.which_activity,
           'time':self.time,
           'input':self.activity_data
       }

class BlackList(Base):
    __tablename__ ="BlackList"
    id = Column(Integer, primary_key=True, autoincrement = True)
    token = Column(String(100), nullable = False)
    b_time = Column(DateTime, default =datetime.utcnow)

    
engine = create_engine('sqlite:///blog.db')
 
Base.metadata.create_all(engine)