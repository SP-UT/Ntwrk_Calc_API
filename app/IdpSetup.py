import boto3

client = boto3.client('cognito-idp')

def create_pool():
    try:
        response = client.create_user_pool(PoolName='CGNTO-IDP')
        print('CGNTO-IDP Cognito UserPool created successfully.')
        return(response['UserPool']['Id'])
    except Exception as e:
        print(e)

def delete_pool(PoolId):
    try:
        response = client.delete_user_pool(UserPoolId=PoolId)
        print(f'{PoolId} Cognito UserPool deleted successfully.')
    except Exception as e:
        print(e)

def UserPoolSetup():
    user_pools = client.list_user_pools(MaxResults=10)['UserPools']
    if not user_pools:
        poolid = create_pool()
    for pool in user_pools:
        if not 'CGNTO-IDP' in pool['Name']:
            poolid = create_pool()
        else:
            print('CGNTO-IDP Pool already created.')
    return (poolid)

def DelPoolSetup():
    user_pools = client.list_user_pools(MaxResults=10)['UserPools']
    for pool in user_pools:
        if 'CGNTO-IDP' in pool['Name']:
            delete_pool(pool['Id'])
        else:
            print('CGNTO-IDP Pool already deleted.')

def PoolExists():
    user_pools = client.list_user_pools(MaxResults=10)['UserPools']
    for pool in user_pools:
        if 'CGNTO-IDP' in pool['Name']:
            return ({"identity_setup_valid": True})
        else:
            return ({"identity_setup_valid": False})

def create_app_client(poolid):
    try:
        app_client = client.create_user_pool_client(
            UserPoolId=poolid,
            ClientName='Ntwrk_Calc_API',
            ExplicitAuthFlows=['ADMIN_NO_SRP_AUTH','USER_PASSWORD_AUTH'],
        )
    except Exception as e:
        print(e)
    return(app_client['UserPoolClient']['ClientId'])

def create_user(Pool_id,uname,email,maction='RESEND',delivery=['EMAIL']):
    try:
        user_create = client.admin_create_user(
            UserPoolId=Pool_id,
            Username=uname,
            DesiredDeliveryMediums=delivery,
            #MessageAction=maction,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                                {
                    'Name': 'email_verified',
                    'Value': 'true'
                },
            ]       
        )
    except Exception as e:
        print(e)
        
def describe_client(poolId, client_id):
    try:
        response = client.describe_user_pool_client(
            UserPoolId=poolId,
            ClientId=client_id
        )
    except Exception as e:
        print(e)
    return(response)

def validate_client_id(poolId, client_id):
    client_details = describe_client(poolId, client_id)
    if client_id == client_details['UserPoolClient']['ClientId']:
        return({"identity_client_valid": True})
    else:
        return({"identity_client_valid": False})
