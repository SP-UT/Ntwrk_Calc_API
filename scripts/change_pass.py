import boto3, argparse

client = boto3.client('cognito-idp')

def admin_set_password(PoolId: str, uname: str, passwd: str):
    try:
        response = client.admin_set_user_password(
            UserPoolId=PoolId,
            Username=uname,
            Password=passwd,
            Permanent=True
        )
    except Exception as e:
        print(e)

parser = argparse.ArgumentParser(description='Set a new permanent password for a Cognito IDOP user in a specific pool.')
parser.add_argument('--poolId', '-pid',
    dest='poolId',
    help="Cognito IDP Pool ID.",
    type=str )
parser.add_argument('--userid', '-u',
    dest='userid',
    help="Cognito IDP Username.",
    type=str )
parser.add_argument('--password', '-p',
    dest='passwd',
    help="Cognito IDP Password",
    type=str )
args = parser.parse_args()
admin_set_password(args.poolId, args.userid, args.passwd)

