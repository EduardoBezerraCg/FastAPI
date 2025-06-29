# from fastapi import status, APIRouter, HTTPException, Depends

# from typing import List

# router = APIRouter(
#     prefix="/users",
#     tags=["Users Section/Properties"],
#     responses={404: {"description": "Not found"}}
# )

# #from genSinteticData import generate_sintetic_data
# from app.utils import hash
# from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery
# from .. import schemas

# #SQL Alchemy part
# from app.db import models
# from app.db.databaseSQLAlchemy import engine
# from .. import schemas, oauth2

# #cache redis
# from redis.asyncio import Redis

# redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=True)
# #if you're using container, instead of local host change to the name of your container...


# ############################       Users part        ######################################

# @router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.UserOut])
# def get_users(current_user: dict = Depends(oauth2.get_current_user)):
#     return makeQuery("""
#         SELECT * FROM users ORDER BY id;
#     """) 

# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
# def create_user(user: schemas.UserCreate):
#     #Hash the password
#     hashed_password = hash(user.password)
#     user.password = hashed_password

#     new_user = makeWriteQuery("""
#         INSERT INTO users (email, password)
#         VALUES (%s, %s) RETURNING *; 
#                               """,(user.email, user.password))  
#     return new_user


# @router.get("/specificUser/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
# def get_user(id: int, current_user: dict = Depends(oauth2.get_current_user)):
#     user = makeQueryBySpecificValue(""" 
#             SELECT * FROM users WHERE id = %s;
#             """, (id,))
#     return user

from fastapi import status, APIRouter, HTTPException, Depends
from typing import List
import json
import asyncio
from datetime import timedelta

router = APIRouter(
    prefix="/users",
    tags=["Users Section/Properties"],
    responses={404: {"description": "Not found"}}
)

from app.utils import hash
from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery
from .. import schemas

#SQL Alchemy part
from app.db import models
from app.db.databaseSQLAlchemy import engine
from .. import schemas, oauth2

#cache redis
from redis.asyncio import Redis

# Update this to your container name if running in Docker
redis_client = Redis(host="redis", port=6379, db=0, decode_responses=True)

# Cache configuration
CACHE_TTL = 300  # 5 minutes
USER_CACHE_KEY = "users:all"
USER_CACHE_KEY_PREFIX = "user:"

############################       Helper Functions        ######################################

async def get_redis_client():
    """Get Redis client with connection validation"""
    try:
        await redis_client.ping()
        return redis_client
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return None

async def cache_user(user_id: int, user_data: dict):
    """Cache individual user data"""
    try:
        client = await get_redis_client()
        if client:
            cache_key = f"{USER_CACHE_KEY_PREFIX}{user_id}"
            await client.setex(
                cache_key, 
                CACHE_TTL, 
                json.dumps(user_data, default=str)
            )
    except Exception as e:
        print(f"Error caching user {user_id}: {e}")

async def get_cached_user(user_id: int):
    """Get cached user data"""
    try:
        client = await get_redis_client()
        if client:
            cache_key = f"{USER_CACHE_KEY_PREFIX}{user_id}"
            cached_data = await client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
    except Exception as e:
        print(f"Error retrieving cached user {user_id}: {e}")
    return None

async def cache_all_users(users_data: list):
    """Cache all users data"""
    try:
        client = await get_redis_client()
        if client:
            await client.setex(
                USER_CACHE_KEY, 
                CACHE_TTL, 
                json.dumps(users_data, default=str)
            )
    except Exception as e:
        print(f"Error caching all users: {e}")

async def get_cached_all_users():
    """Get cached all users data"""
    try:
        client = await get_redis_client()
        if client:
            cached_data = await client.get(USER_CACHE_KEY)
            if cached_data:
                return json.loads(cached_data)
    except Exception as e:
        print(f"Error retrieving cached users: {e}")
    return None

async def invalidate_user_cache(user_id: int = None):
    """Invalidate user cache(s)"""
    try:
        client = await get_redis_client()
        if client:
            print("Invalidating user cache...")
            # Always invalidate all users cache
            await client.delete(USER_CACHE_KEY)
            
            # If specific user ID provided, invalidate that too
            if user_id:
                cache_key = f"{USER_CACHE_KEY_PREFIX}{user_id}"
                await client.delete(cache_key)
    except Exception as e:
        print(f"Error invalidating cache: {e}")

############################       Users part        ######################################

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.UserOut])
async def get_users(current_user: dict = Depends(oauth2.get_current_user)):
    # Try to get from cache first
    cached_users = await get_cached_all_users()
    if cached_users:
        print("Returning users from cache")
        return cached_users
    
    # If not in cache, query database
    print("Fetching users from database")
    users = makeQuery("""
        SELECT * FROM users ORDER BY id;
    """)
    
    # Cache the result
    if users:
        await cache_all_users(users)
    
    return users

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate):
    #Hash the password
    hashed_password = hash(user.password)
    user.password = hashed_password

    new_user = makeWriteQuery("""
        INSERT INTO users (email, password)
        VALUES (%s, %s) RETURNING *; 
                              """,(user.email, user.password))  
    
    # Invalidate cache after creating new user
    await invalidate_user_cache()
    
    # Cache the new user
    if new_user and 'id' in new_user:
        await cache_user(new_user['id'], new_user)
    
    return new_user

@router.get("/specificUser/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
async def get_user(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    # Try to get from cache first
    cached_user = await get_cached_user(id)
    if cached_user:
        print(f"Returning user {id} from cache")
        return cached_user
    
    # If not in cache, query database
    print(f"Fetching user {id} from database")
    user = makeQueryBySpecificValue(""" 
            SELECT * FROM users WHERE id = %s;
            """, (id,))
    
    # Cache the result if user exists
    if user:
        await cache_user(id, user)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} was not found"
        )

# @router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
# async def update_user(id: int, user: schemas.UserUpdate, current_user: dict = Depends(oauth2.get_current_user)):
#     # Check if user exists
#     existing_user = makeQueryBySpecificValue("""
#         SELECT * FROM users WHERE id = %s;
#     """, (id,))
    
#     if not existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"User with id: {id} was not found"
#         )
    
#     # Update user
#     update_data = user.dict(exclude_unset=True)
#     if 'password' in update_data:
#         update_data['password'] = hash(update_data['password'])
    
#     # Build dynamic update query
#     set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
#     values = list(update_data.values()) + [id]
    
#     updated_user = makeWriteQuery(f"""
#         UPDATE users SET {set_clause}
#         WHERE id = %s RETURNING *;
#     """, tuple(values))
    
#     # Invalidate cache after update
#     await invalidate_user_cache(id)
    
#     return updated_user

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    # Check if user exists
    user = makeQueryBySpecificValue("""
        SELECT * FROM users WHERE id = %s;
    """, (id,))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} was not found"
        )
    
    # Delete user
    makeWriteQuery("""
        DELETE FROM users WHERE id = %s;
    """, (id,))
    
    # Invalidate cache after deletion
    await invalidate_user_cache(id)

############################       Cache Management Endpoints        ######################################

@router.delete("/cache/clear", status_code=status.HTTP_200_OK)
async def clear_user_cache(current_user: dict = Depends(oauth2.get_current_user)):
    """Clear all user-related cache"""
    try:
        client = await get_redis_client()
        if client:
            # Get all user cache keys
            pattern = f"{USER_CACHE_KEY_PREFIX}*"
            keys = await client.keys(pattern)
            keys.append(USER_CACHE_KEY)  # Add the all users cache key
            
            if keys:
                await client.delete(*keys)
                return {"message": f"Cleared {len(keys)} cache entries"}
            else:
                return {"message": "No cache entries found"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis connection not available"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )

@router.get("/cache/status", status_code=status.HTTP_200_OK)
async def get_cache_status(current_user: dict = Depends(oauth2.get_current_user)):
    """Get cache status and statistics"""
    try:
        client = await get_redis_client()
        if client:
            # Get cache info
            pattern = f"{USER_CACHE_KEY_PREFIX}*"
            user_keys = await client.keys(pattern)
            all_users_exists = await client.exists(USER_CACHE_KEY)
            
            return {
                "redis_connected": True,
                "individual_users_cached": len(user_keys),
                "all_users_cached": bool(all_users_exists),
                "cache_ttl_seconds": CACHE_TTL
            }
        else:
            return {
                "redis_connected": False,
                "message": "Redis connection not available"
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting cache status: {str(e)}"
        )