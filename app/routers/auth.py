import os
from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import db, schemas, cognito
from ..config import settings

router = APIRouter(
    tags=['Authentication']
    )

@router.post('/login', response_model=schemas.UserOut)
def login(user_credentials: OAuth2PasswordRequestForm = Depends() , db: Session = Depends(db.initialize_db)):
    try:
        login = cognito.admin_init_auth(
            UserPoolId=os.environ.get('COGNITO_POOL_ID'),
            ClientId=os.environ.get('APP_CLIENT_ID'),
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': user_credentials.username,
                'PASSWORD': user_credentials.password
            }
        )
        if "ChallengeName" in login.keys() and login['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
            detail=f"{login['ChallengeName']}")
    except cognito.client.exceptions.ResourceNotFoundException as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
            detail="ResourceNotFoundException")
    except cognito.client.exceptions.InvalidParameterException as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
            detail="InvalidParameterException")
    except cognito.client.exceptions.NotAuthorizedException as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
            detail="NotAuthorizedException")
    except cognito.client.exceptions.TooManyRequestsException as e:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS,
            detail="TooManyRequestsException")
    except cognito.client.exceptions.InternalErrorException as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="InternalErrorException")
    except cognito.client.exceptions.ForbiddenException as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
            detail="ForbiddenException")
    return {
        'access_token' : login['AuthenticationResult']['AccessToken'],
        'token_type' : login['AuthenticationResult']['TokenType'],
        'expires_in' : login['AuthenticationResult']['ExpiresIn'],
        'refresh_token' : login['AuthenticationResult']['RefreshToken'],
        'token_id' : login['AuthenticationResult']['IdToken']
    }

# @router.post('/passwd', response_model=schemas.ChangePasswordOut)
# def passwd_change(details: schemas.UserChangePassword, db: Session = Depends(db.initialize_db)):
#     try:
# Get user details and identify if this is the right user.
#         cognito.user_change_password(
#             token = details.
#             curr_password = 
#             new_password = 
#         )
