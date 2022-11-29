import boto3

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

def user_change_password(token: str, curr_password: str, new_password: str):
    passwd_change = client.change_password(
        PreviousPassword=curr_password,
        ProposedPassword=new_password,
        AccessToken=token
    )
    return(passwd_change)
