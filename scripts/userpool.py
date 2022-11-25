import boto3

client = boto3.client('cognito-idp')

def create_pool():
    try:
        response = client.create_user_pool(PoolName='CGNTOIDP')
        print('CGNTOIDP created successfully.')
    except Exception as e:
        print(e)

def delete_pool(PoolId):
    try:
        response = client.delete_user_pool(UserPoolId=PoolId)
        print('CGNTOIDP deleted successfully.')
    except Exception as e:
        print(e)

def UserPoolSetup():
    user_pools = client.list_user_pools(MaxResults=10)['UserPools']
    if not user_pools:
         create_pool()
    for pool in user_pools:
        if not 'CGNTOIDP' in pool['Name']:
            create_pool()
        else:
            print('CGNTOIDP Pool already created.')

def DelPoolSetup():
    user_pools = client.list_user_pools(MaxResults=10)['UserPools']
    for pool in user_pools:
        if 'CGNTOIDP' in pool['Name']:
            delete_pool(pool['Id'])
        else:
            print('CGNTOIDP Pool already deleted.')


#UserPoolSetup()
#DelPoolSetup()
