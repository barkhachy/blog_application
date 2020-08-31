from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from model import User, Blog, Comment

engine = create_engine('sqlite:///blog.db')

with engine.connect() as con:

    con.execute('''CREATE TRIGGER Delete_USER_trigger
    AFTER DELETE ON USER
    FOR EACH ROW
    BEGIN
        DELETE FROM BLOG WHERE AUTHOR = OLD.USER_NAME;
        DELETE FROM COMMENT WHERE AUTHOR = OLD.USER_NAME;
    END''')

    con.execute('''CREATE TRIGGER Delete_POST_trigger
    AFTER DELETE ON BLOG
    FOR EACH ROW
    BEGIN
        DELETE FROM COMMENT WHERE BLOG_ID = OLD.BLOG_ID;
    END''')
