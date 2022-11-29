import os
from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import db, schemas, cognito

router = APIRouter(
    tags=['Authentication']
    )

@router.post('/login', response_model=schemas.UserOut)
def login(user_credentials: OAuth2PasswordRequestForm = Depends() , db: Session = Depends(db.initialize_db)):
    #table = db.Table(f'{settings.auth_table}')
    # login = cognito.admin_init_auth(
    #     UserPoolId=os.environ.get('COGNITO_POOL_ID'),
    #     ClientId=os.environ.get('APP_CLIENT_ID'),
    #     AuthFlow='ADMIN_USER_PASSWORD_AUTH',
    #     AuthParameters={
    #         'USERNAME': user_credentials.username,
    #         'PASSWORD': user_credentials.password
    #     }
    # )
    # print(login)
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
    except Exception as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 
            detail=f"Invalid Credentials"
            )
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
#         cognito.user_change_password(
#             token = details.
#             curr_password = 
#             new_password = 
#         )
