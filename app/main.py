from fastapi import FastAPI,Response,status,HTTPException
from fastapi import Body,Depends
from pydantic import BaseModel
from typing  import Optional
from  random  import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine,get_db
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)

app=FastAPI()


my_posts=[{"title":"title for the first one","content":"content for the first one","id":1},{"title":"title for the second one","content":"content for the second one","id":2}]

def find_post(id):
    for p in my_posts:
        if p["id"]==id:
            return p
        
def delete_post(id):
    for p in my_posts:
        if p["id"]==id:
            my_posts.remove(p)
            return p
        
def find_index(id):
    for  i,p in enumerate(my_posts):
        if p['id']==id:
            return i

class Post(BaseModel):
    title: str
    content: str
    published: bool=True
    

while True:
    try:
        conn=psycopg2.connect(host='localhost',database='customAPI',user='postgres',password='pass123',cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("database connected  successfully.")
        break
    except Exception as error:
        print("connecting to the database failed")
        print("Error:",error)
        time.sleep(2)


@app.get("/")   #decorator
async def root():  #async is optional here
    return {"message":"hello GARIMA"}

@app.get("/sqlalchemy")
def test_posts(db: Session=Depends(get_db)):
    posts=db.query(models.Post).all()
    return{"data":posts}


@app.get("/posts")
def get_posts(db: Session=Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts=cursor.fetchall()
    posts=db.query(models.Post).all()
    print(posts)
    return {"data":posts}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(post:Post,db: Session=Depends(get_db)):
#    cursor.execute("""INSERT INTO posts(title,content,published)VALUES (%s,%s,%s)RETURNING *""",(post.title,post.content,post.published))
#    post_dict=cursor.fetchone()
#    conn.commit() 
   new_post=models.Post(**post.dict())
   db.add(new_post)
   db.commit()
   db.refresh(new_post)
   return {"data":new_post}

@app.get("/posts/{id}")
def get_post(id:int,db: Session=Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id=%s""",(str(id)))
    # post=cursor.fetchone() 
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id} was not found")
    return{"data":post}

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def deleteid(id:int,db: Session=Depends(get_db)):
    # dp=cursor.execute("""DELETE FROM posts  WHERE id=%s RETURNING *""",(str(id)))
    # post=cursor.fetchone()
    # conn.commit()
    post=db.query(models.Post).filter(models.Post.id==id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{id} not found")
    post.delete(synchronize_session=False)
    db.commit()
    return {"deleted":f"{id}"}

@app.put("/posts/{id}")
def update_post(id:int,post:Post):
    cursor.execute("""UPDATE posts SET title=%s,content=%s,published=%s WHERE id=%s RETURNING*""",(post.title,post.content,post.published,str(id)))
    postt=cursor.fetchone()
    conn.commit()
    if  not postt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="does not exist.")
    
    return{"message":postt}

