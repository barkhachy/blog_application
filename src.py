import os
import sys
from model.model import Base, User, Blog, Comment, Audit
from flask import request, json, Response, Blueprint, g, Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Auth.Authentication import Auth
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = str(os.getcwd()) + '/files/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
engine = create_engine('sqlite:///blog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/signup' , methods = ['POST'])
def create():
    """
      Signup for user
    """
    print(request)
    json = request.get_json()
    #json = request.data()
    print(json['user_name'])
    if json['user_name'] is None or json['password'] is None or json['e_mail'] is None or json['name'] is None :
        message = {'error': 'Provide all Details!!!'}
        return custom_response(message, 400)
    query = db_session.query(User).filter_by(user_name = json['user_name']).first()
    #print(query)
    if query is not None : 
        message = {'error': 'User already exist, please supply another email address'}
        return custom_response(message, 400)
    try:
      user = User(user_name = json['user_name'], e_mail = json['e_mail'], name = json['name'])
      user.hash_password(json['password'])
      db_session.add(user)
      db_session.commit()   
      token = Auth.generate_token(json['user_name'])
      audit = Audit(user_name = json['user_name'], activity = request.method, which_activity = sys._getframe().f_code.co_name , activity_data = str(json))
      db_session.add(audit)
      db_session.commit()
      return custom_response({'jwt_token': token}, 201)
    except Exception as e:
      return custom_response("some error happended!!",400) 
    
    
@app.route('/login', methods=['POST'])
def login():
  """
  User Login Function
  """
  req_data = request.get_json()
  if req_data['user_name'] is None or req_data['password'] is None :
    return custom_response({'error': 'you need email and password to sign in'}, 400)
  query = db_session.query(User).filter_by(user_name = req_data['user_name']).first()
  if query is None:
    return custom_response({'error': 'Signup First!!'}, 400)
  if not query.verify_password(req_data['password']):
    return custom_response({'error': 'Wrong Password!!'}, 400)
  token = Auth.generate_token(req_data['user_name'])
  audit = Audit(user_name = json['user_name'], activity = request.method, which_activity = sys._getframe().f_code.co_name )
  db_session.add(audit)
  db_session.commit()
  return custom_response({'jwt_token': token}, 200)

@app.route('/users', methods = ['GET'])
@Auth.auth_required
def all_users():
  query = db_session.query(User).all()
  user = []
  for i in query:
    obj = {
      "name":i.name,
      "user_name":i.user_name,
      "e_mail":i.e_mail
    }
    user.append(obj)
  audit = Audit(user_name = g.user.get('id'), activity = request.method, which_activity = sys._getframe().f_code.co_name )
  db_session.add(audit)
  db_session.commit()
  return custom_response(user, 200)

@app.route('/logout', methods = ['POST'])
@Auth.auth_required
def logout():
  """
    Logout
  """
  audit = Audit(user_name = str(g.user.get('id')), activity = request.method, which_activity = sys._getframe().f_code.co_name )
  db_session.add(audit)
  db_session.commit()
  return custom_response("Logged out",200)

@app.route('/me', methods = ['GET'])
@Auth.auth_required
def show_details():
  """
    To get own details
  """
  query = db_session.query(User).filter_by(user_name = str(g.user.get('id'))).one()
  #print(query)
  json = {
    "user_name" : g.user.get('id'),
    "Full Name": query.name,
    "e_mail" : query.e_mail
  }
  audit = Audit(user_name = str(g.user.get('id')), activity = request.method, which_activity = sys._getframe().f_code.co_name)
  db_session.add(audit)
  db_session.commit()
  return custom_response(json, 200)

@app.route('/me', methods = ['PUT'])
@Auth.auth_required
def update_details():
  query = db_session.query(User).filter_by(user_name = g.user.get('id')).one()
  req_data = request.get_json()
  data = ""
  if 'name' in req_data:
    query.name = req_data['name']
    db_session.add(query)
    db_session.commit()
    data = data +'{ name :'+req_data['name']+' },'
  if 'e_mail' in req_data:
    query.e_mail = req_data['e_mail']
    db_session.add(query)
    db_session.commit()
    data = data +'{ e_mail :'+req_data['e_mail']+' },'
  if 'password' in req_data:
    query.hash_password(req_data['password'])
    db_session.add(query)
    db_session.commit()
  audit = Audit(user_name = str(g.user.get('id')), activity = request.method, which_activity = sys._getframe().f_code.co_name, activity_data = data)
  db_session.add(audit)
  db_session.commit()
  return custom_response("updated", 200)

@app.route('/me', methods = ['DELETE'])
@Auth.auth_required
def delete():
  audit = Audit(user_name = str(g.user.get('id')), activity = request.method, which_activity = sys._getframe().f_code.co_name)
  db_session.add(audit)
  db_session.commit()
  try:
    db_session.query(User).filter_by(user_name = g.user.get('id')).delete()
    db_session.commit()
  except Exception as e:
    print(e)
    print("error is here")
  return custom_response("deleted!!",200)
@app.route('/blogs', methods=['GET'])
@Auth.auth_required
def get_all_blogs():
  """
  Get all blogs
  """
  query = db_session.query(Blog).all()
  blogs = [i.serialize for i in query]
  
  audit = Audit(user_name = str(g.user.get('id')), activity = request.method, which_activity = sys._getframe().f_code.co_name)
  db_session.add(audit)
  db_session.commit()
  return custom_response(blogs, 200)

@app.route('/blogs', methods = ['POST'])
@Auth.auth_required
def add_new_blog():
  """
    Create new blog
  """
  path = ""
  if 'file' in request.files:
    file = request.files['file']
    
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      path = os.path.join(app.config['UPLOAD_FOLDER'])+file.filename
      print(path)
  new_entry = Blog(author = g.user.get('id'), title = request.form['title'], description = request.form['description'], body = request.form['body'], image = path)
  db_session.add(new_entry)
  db_session.commit()
  js = {
    'title':request.form['title'],
    'author':g.user.get('id'),
    'description':request.form['description'],
    'body':request.form['body']
  }
  audit = Audit(user_name = str(g.user.get('id')), activity = request.method, which_activity = sys._getframe().f_code.co_name , activity_data = str(js))
  db_session.add(audit)
  db_session.commit()
  return custom_response("Blog created", 200)

@app.route('/blogs/<int:blog_id>', methods = ['PUT'])
@Auth.auth_required
def update_blog(blog_id):
  """
    To update someone blog
  """
  path = ""
  di = ""
  query = db_session.query(Blog).filter_by(blog_id = blog_id).one()
  if query.author != g.user.get('id'):
    return custom_response("You can't update other's post")
  if 'file' in request.files:
    file = request.files['file']
    
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      path = os.path.join(app.config['UPLOAD_FOLDER'])+file.filename
      print(path)
      query.image = path
      db_session.add(query)
      db_session.commit()
      di = di+ '{ image : '+ path +'},'
    
  print(query.image)
  query = db_session.query(Blog).filter_by(blog_id = blog_id).one()
  print(query.image)
  print(query.description)
  if query.author != g.user.get('id'):
    return custom_response("You can't update someone's blog",400)
  li = []
  for i in request.form:
    li.append(i)
  if 'title' in li:
    query.title = request.form['title']
    db_session.add(query)
    db_session.commit()
    di = di+ '{ title : '+ request.form['title'] +'},'

  if 'body' in li:
    query.body = request.form['body']
    db_session.add(query)
    db_session.commit()
    di = di+ '{ body : '+ request.form['body'] +'},'

  if 'description' in li:
    query.body = request.form['description']
    db_session.add(query)
    db_session.commit()
    di = di+ '{ description : '+ request.form['description'] +'},'
  #query.description = request.form['description']
  
  audit = Audit(user_name = g.user.get('id'), activity = request.method, which_activity = sys._getframe().f_code.co_name, activity_data = di)
  db_session.add(audit)
  return custom_response("okk!!",200)


@app.route('/blogs/<int:blog_id>', methods = ['DELETE'])
@Auth.auth_required
def delete_blog(blog_id):
  """ To delete blog """

  query = db_session.query(Blog).filter_by(blog_id = blog_id).one()
  if query.author != g.user.get('id'):
    return custom_response("Not Authorized to delete someone's post",200)
  
  db_session.delete(query)
  db_session.commit()
  audit = Audit(user_name = g.user.get('id'), activity = request.method, which_activity = sys._getframe().f_code.co_name)
  db_session.add(audit)
  return custom_response("okk!!",200)

@app.route('/blogs/<int:blog_id>/comments', methods = ['GET'])
@Auth.auth_required
def all_comments(blog_id):
  """
    To view all comments
  """
  query = db_session.query(Comment).filter_by(blog_id = blog_id).all()
  comments = [i.serialize for i in query]
  audit = Audit(user_name = g.user.get('id'), activity = request.method, which_activity = sys._getframe().f_code.co_name)
  db_session.add(audit)
  return custom_response(comments, 200)

@app.route('/blogs/<int:blog_id>/comments', methods = ['POST'])
@Auth.auth_required
def add_comment(blog_id):
  """
    To add new comment to blog
  """
  req_data = request.get_json()
  new_entry = Comment(blog_id = blog_id, author = g.user.get('id'), body = req_data['body'])
  db_session.add(new_entry)
  db_session.commit()
  audit = Audit(user_name = g.user.get('id'), activity = request.method, which_activity = sys._getframe().f_code.co_name , activity_data = str(req_data))
  db_session.add(audit)
  return custom_response("Comment added", 200)

@app.route('/blogs/<int:blog_id>/comments/<int:comment_id>', methods = ['DELETE'])
@Auth.auth_required
def delete_comment(blog_id, comment_id):
  """
    To delete own comment
  """
  query = db_session.query(Comment).filter_by(comment_id = comment_id).one()
  if query.author != g.user.get('id'):
    return custom_response("You can't delete someone's comment",200)

  db_session.delete(query)
  db_session.commit()
  audit = Audit(user_name = g.user.get['id'], activity = request.method, which_activity = sys._getframe().f_code.co_name )
  db_session.add(audit)
  return custom_response("comment deleted ",200)

@app.route('/blogs/<int:blog_id>/comments/<int:comment_id>', methods = ['PUT'])
@Auth.auth_required
def update_comment(blog_id, comment_id):
  """
    To update own comment
  """
  req_data = request.get_json()
  print(req_data)
  query = db_session.query(Comment).filter_by(comment_id = comment_id).one()
  if query.author != g.user.get('id'):
    return custom_response("You can't update someone's comment",200)
  query.body = req_data['body']
  db_session.add(query)
  db_session.commit()
  audit = Audit(user_name = g.user.get('id'), activity = request.method, which_activity = sys._getframe().f_code.co_name , activity_data = str(req_data))
  db_session.add(audit)
  return custom_response("comment changed ",200)

@app.route('/audits', methods = ['GET'])
@Auth.auth_required
def show_audit():
  query = db_session.query(Audit).all()
  audit = [i.serialize for i in query]
  return custom_response(audit, 200)


def custom_response(res, status_code):
  """
  Custom Response Function
  """
  print(res)
  return Response(
    mimetype = "application/json",
    response = json.dumps(res),
    status = status_code
  )

if __name__=="__main__":
    app.debug = True
    app.run(host = "0.0.0.0",port = 5000)

