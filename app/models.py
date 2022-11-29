from .db import initialize_db
from .config import settings
import boto3

def generate_networks(ddb,table_name):
    client = boto3.client('dynamodb', region_name=f'{settings.region_name}')
    existing_tables = client.list_tables()
    if table_name not in existing_tables['TableNames']: 
        ddb.create_table(
            TableName=table_name,
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
    print(f'Successfully created table {table_name}')

def drop_networks(ddb,table_name):
    table = ddb.Table(table_name)
    try:
        table.delete()
        print(f'{table_name} Dynamo DB Table deleted successfully.')
    except Exception as e:
        print(e)

def generate_table():
    ddb = initialize_db()
    generate_networks(ddb,settings.ddb_table)
    generate_networks(ddb,settings.cidr_table)

def drop_table():
    ddb = initialize_db()
    drop_networks(ddb,settings.ddb_table)
    drop_networks(ddb,settings.cidr_table)
