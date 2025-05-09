
from fastapi import status, APIRouter, HTTPException

from typing import List

from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery
from .. import schemas, oauth2
from fastapi import Depends


router = APIRouter(
    prefix="/posts",
    tags=["Social media posts"],
    responses={404: {"description": "Not found"}}
)

############################       Posts part        ######################################
#Get posts
@router.get("/", status_code=status.HTTP_200_OK,response_model=List[schemas.PostResponse])
def get_posts(current_user: dict = Depends(oauth2.get_current_user)):
    print("Requested by:", current_user["email"])
    return makeQuery("""
        SELECT * FROM posts ORDER BY id;
    """)    
    

#Get post by ID
@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_post(id: int, current_user: dict = Depends(oauth2.get_current_user)):

    print("Requested by:", current_user["email"])

    post = makeQueryBySpecificValue("""
                                    
                                    SELECT * FROM posts WHERE id = %s;

                                    """, (id,))
    return {"post_detail": post}




#Post(create) a post
@router.post("/create", response_model=schemas.PostResponse)
def create_post(
    post: schemas.PostCreate,
    current_user: dict = Depends(oauth2.get_current_user)  # Só para autenticação!
):
    create_post_query = makeWriteQuery("""
        INSERT INTO posts (title, content, published, owner_id)
        VALUES (%s, %s, %s,%s) RETURNING *;
    """, (post.title, post.content, post.published, current_user["id"]))  

    #Debug  
    print("Requested by:", current_user["email"])
    return create_post_query


#Delete
@router.delete("/makeDeletions/{id}",status_code=204)
def delete_post(id:int, current_user: dict = Depends(oauth2.get_current_user)):
    postDelete = makeWriteQuery("DELETE FROM public.posts WHERE id = %s RETURNING *;", (id,))

    if postDelete != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    return {"detail": "Post deleted"}



#UpdatePosts
@router.put("/makeUpdates/{id}")
def update_post(id:int, post: schemas.PostCreate, current_user: dict = Depends(oauth2.get_current_user)):

    update_query = """
    UPDATE posts
    SET title = %s, content = %s, published = %s
    WHERE id = %s
    RETURNING *;
"""

    updated_post = makeWriteQuery(update_query, (post.title, post.content, post.published, id))

    return updated_post