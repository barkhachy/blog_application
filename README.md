<h1 align="center">Blog Application</h1>

<h4>A REST API service for a Blog Application where users can</h4>
  <ul>
    <li>create their account,delete it
    <li>create blogs(picture can be uploaded on server)
    <li>update and delete their own blogs
    <li>view blogs created by others
    <li>add comment on blog, view all comments
    <li>edit and delete their own comments
  <ul><br><br>
    
    Two different parts of this project:
      1. Backend(Flask)
      2. Database(SQL)
  <br><br>
  To successfully run this application you can clone this repo.
  <br>
    1. Install all dependecies<br>
      `pip install -r requirements.txt `<br>
    2. Run the application<br>
      `python src.py`<br>
    3. Connect to : `localhost:5000`<br>
    
  How to use?<br>
    1. `/signup` to create a account with attributes in json format `user_name, name, e_mail, password`.<br>
    2. `/login` to login with credentials in json format `user_name, password`<br>
    3. `/me` to do all account related operations.<br>
    4. `/users` to get all users details `user_name, name, e_mail `<br>
    5. `/blogs` to view all blogs with 'GET'<br>
    6. `/blogs` to create new blogs with 'POST' Method<br>
    7. `/blogs/id` to edit or delete own blog with blog_id<br>
    8. `/blogs/id/comments` to add or view comment on particular blog<br>
    9. `/blogs/id/comments/comment_id` to view or delete comment if they are the owner of that comment<br>
  
  <h4> Here we have also audit table to store all user's event</h4><br>
  
                                  `Future scope to reduce the latency` 
