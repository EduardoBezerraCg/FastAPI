import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException

from app.core.config import settings

def get_connection():
    return psycopg2.connect(
        host=settings.db_host,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        port=settings.db_port,
    )

def makeQuery(query: str):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

        if not results:
            raise HTTPException(status_code=400, detail=f"No results for the query: {query}")
        
        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar banco de dados: {e}")
    
def makeQueryBySpecificValue(query: str, params: tuple = ()):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchone()

        if not results:
            raise HTTPException(status_code=404, detail="No results for the specific value, make sure that this value exists")

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar banco de dados: {e}")

    
def makeWriteQuery(query: str, params: tuple = ()):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchone()
                conn.commit()

        if not results:
            raise HTTPException(status_code=400, detail="Write action for the specific value is not allowed, make sure that this value exists")

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar banco de dados: {e}")


def validate_post_ownership(post_id: int, current_user_id: int):
    post = makeQueryBySpecificValue("SELECT * FROM public.posts WHERE id = %s;", (post_id,))

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post = post[0] if isinstance(post, list) else post

    if int(post["owner_id"]) != int(current_user_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this post, make sure that you are the owner")

    return post