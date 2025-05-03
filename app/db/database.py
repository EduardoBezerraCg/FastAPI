import psycopg2
from psycopg2.extras import RealDictCursor
import os
from fastapi import FastAPI, HTTPException, status

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "fastapi"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        port=os.getenv("DB_PORT", 5432)
    )

def makeQuery(query: str):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

        if not results:
            raise HTTPException(status_code=400, detail=f"No results for the query: {query}")
        
        return {"data": results}

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
            raise HTTPException(status_code=404, detail="Post not found")

        return {"data": results}

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

        return {"data": results}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar banco de dados: {e}")
