import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
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

    blog_id = Column(Integer, primary_key = True)
    author = Column(String(30),ForeignKey('User.user_name'))
    title = Column(String(30),nullable=False)
    body = Column(String(40))
    description = Column(String(250),nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    link = Column(String(50))
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
           'link':self.link
       }
 
class Comment(Base):
    __tablename__ = 'Comment'

    comment_id = Column(Integer, primary_key = True)
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

engine = create_engine('sqlite:///blog.db')
 
Base.metadata.create_all(engine)