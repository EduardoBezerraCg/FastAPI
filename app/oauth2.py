from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import schemas
from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("Token criado:", encoded_jwt)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Payload decodificado:", payload)
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        #token_data = schemas.TokenData(id=id)
        token_data = schemas.TokenData(id=str(id))

    except JWTError:
        raise credentials_exception
    
    return token_data
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    print("Token recebido:", token)
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},
                                        )

    # Step 1: Verify token and extract user_id
    token = verify_access_token(token, credentials_exception)

    # Step 2: Query user by ID
    user_query = "SELECT * FROM users WHERE id = %s"
    #user = makeQueryBySpecificValue(user_query, (token["id"],))
    user = makeQueryBySpecificValue(user_query, (token.id,))
    #print out the user email
    print("User email:", user["email"])

    return user