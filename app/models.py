from .db import initialize_db
from .config import settings
import boto3

def generate_networks(ddb):
    client = boto3.client('dynamodb', region_name=f'{settings.region_name}')
    existing_tables = client.list_tables()
    if f'{settings.ddb_table}' not in existing_tables['TableNames']: 
        ddb.create_table(
            TableName=f'{settings.ddb_table}',
            AttributeDefinitions=[
                {
                    'AttributeName': 'shrt_name',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'shrt_name',
                    'KeyType': 'HASH'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    print(f'Successfully created table {settings.ddb_table}')

def drop_networks(ddb):
    table = ddb.Table(f'{settings.ddb_table}')
    try:
        table.delete()
        print(f'{settings.ddb_table} Dynamo DB Table deleted successfully.')
    except Exception as e:
        print(e)

def generate_table():
    ddb = initialize_db()
    generate_networks(ddb)

def drop_table():
    ddb = initialize_db()
    drop_networks(ddb)
