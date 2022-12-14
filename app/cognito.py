import boto3, time
from cognitojwt import decode

client = boto3.client('cognito-idp')

def admin_init_auth(UserPoolId: str, ClientId: str,AuthFlow: str, AuthParameters: dict):
    admin_auth = client.admin_initiate_auth(
            UserPoolId=UserPoolId,
            ClientId=ClientId,
            AuthFlow=AuthFlow,
            AuthParameters=AuthParameters
        )
    return(admin_auth)

def get_user_details(token: str):
    user_details = client.get_user(
        AccessToken=token
    )
    return(user_details)

def get_jwt_user_details(token: str, region: str, idp_pool: str, client_id: str):
    jwt_user_detail = decode(
            token,
            region,
            idp_pool,
            app_client_id=client_id
        )
    return (jwt_user_detail)

def validate_user_id(token: str, region: str, idp_pool: str, client_id: str):
    try:
        idp_username = get_user_details(token)['Username']
        jwt_username = get_jwt_user_details(
            token,
            region,
            idp_pool,
            client_id
        )['username']
        if idp_username == jwt_username:
         status = {"user_verified": True}
    except Exception as e:
        status = {"user_verified": False}
    return(status)

def is_token_expired(token: str, region: str, idp_pool: str, client_id: str):
    try:
        token_exp =  get_jwt_user_details(
            token,
            region,
            idp_pool,
            client_id
        )['exp']
        token_status = { "token_expired": False }
    except Exception as e:
        token_status = { "token_expired": True }
    return(token_status)

def user_change_password(token: str, curr_password: str, new_password: str):
    passwd_change = client.change_password(
        PreviousPassword=curr_password,
        ProposedPassword=new_password,
        AccessToken=token
    )
    return(passwd_change)
