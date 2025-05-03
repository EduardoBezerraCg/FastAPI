from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery
from .. import schemas, utils


router = APIRouter(
    prefix="/oath2",
    tags=["Users Section/Properties"],
    responses={404: {"description": "Not found"}}
)

#get userfunction
@router.get("/login/getUserDetails/{email}")
def get_user(email: str):
    # Normalize the email (remove spaces, lowercase it)
    normalized_email = email.strip().lower()

    user = makeQueryBySpecificValue("""
        SELECT * 
        FROM public.users
        WHERE LOWER(email) = %s;
    """, (normalized_email,))
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"user": user}


@router.post("/login")
def login(user_credentials: schemas.UserLogin):
    email = user_credentials.email.strip().lower()

    user = makeQueryBySpecificValue("""
        SELECT * 
        FROM public.users
        WHERE LOWER(email) = %s;
    """, (email,))

    print("Usuário do banco:", user)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")

    return {"token": "Example token"}
