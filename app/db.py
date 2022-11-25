import boto3
from boto3.resources.base import ServiceResource
from .config import settings

def initialize_db() -> ServiceResource:
    ddb = boto3.resource('dynamodb',
                         region_name=f'{settings.region_name}',
                         aws_access_key_id=f'{settings.aws_access_key_id}',
                         aws_secret_access_key=f'{settings.aws_secret_access_key}')
    return ddb
