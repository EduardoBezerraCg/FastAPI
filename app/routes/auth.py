from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery
from .. import oauth2, schemas, utils


router = APIRouter(
    prefix="/oath2",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}}
)

#get userfunction
@router.get("/login/getUserDetails/{email}")
def get_user(email: str, current_user: dict = Depends(oauth2.get_current_user)):
    # Normalize the email (remove spaces, lowercase it)
    normalized_email = email.strip().lower()

    user = makeQueryBySpecificValue("""
        SELECT * 
        FROM public.users
        WHERE LOWER(email) = %s;
    """, (normalized_email,))
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"userDetails": f"The email {normalized_email}, is a valid user"}


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):

    email = user_credentials.username.strip().lower()

    user = makeQueryBySpecificValue("""
        SELECT * 
        FROM public.users
        WHERE LOWER(email) = %s;
    """, (email,))

    print("Usuário do banco:", user)

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id": user["id"]})

    return {"access_token": access_token, "token_type": "bearer"}

