
import os
import datetime
import jwt
from flask import json, Response, request, g
from functools import wraps
from model.model import Base, User, Blog, Comment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv


engine = create_engine('sqlite:///blog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class Auth():
  """
  Auth Class
  """
  @staticmethod
  def generate_token(user_name):
    """
    Generate Token Method
    """
    
    try:
      payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_name
      }
      print("PAYLOAD COMPLETED")
      return jwt.encode(
        payload,
        "abcdefgh",
        'HS256'
      ).decode("utf-8")
    except Exception as e:
      print(e)
      return Response(
        mimetype="application/json",
        response=json.dumps({'error': 'error in generating user token'}),
        status=400
      )

  @staticmethod
  def decode_token(token):
    """
    Decode token method
    """
    re = {'data': {}, 'error': {}}
    try:
      payload = jwt.decode(token, "abcdefgh")
      re['data'] = {'user_name': payload['sub']}
      return re
    except jwt.ExpiredSignatureError as e1:
      re['error'] = {'message': 'token expired, please login again'}
      return re
    except jwt.InvalidTokenError:
      re['error'] = {'message': 'Invalid token, please try again with a new token'}
      return re

  # decorator
  @staticmethod
  def auth_required(func):
    """
    Auth decorator
    """
    @wraps(func)
    def decorated_auth(*args, **kwargs):
      if 'api-token' not in request.headers:
        return Response(
          mimetype="application/json",
          response=json.dumps({'error': 'Authentication token is not available, please login to get one'}),
          status=400
        )
      token = request.headers.get('api-token')
      data = Auth.decode_token(token)
      if data['error']:
        return Response(
          mimetype="application/json",
          response=json.dumps(data['error']),
          status=400
        )
        
      user_name = data['data']['user_name']
      check_user = session.query(User).filter_by(user_name = user_name).first()
      if not check_user:
        return Response(
          mimetype="application/json",
          response=json.dumps({'error': 'user does not exist, invalid token'}),
          status=400
        )
      g.user = {'id': user_name}
      return func(*args, **kwargs)
    return decorated_auth