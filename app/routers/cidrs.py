import os
from typing import List
from ipaddress import IPv4Network as ip
from fastapi import status, HTTPException, Depends, APIRouter
from .. import db, schemas, cognito
from sqlalchemy.orm import Session
from ..config import settings
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter(
    tags=['CIDRs']
    )

security = HTTPBearer()

@router.post('/cidrs', status_code=status.HTTP_201_CREATED, response_model=schemas.NewCIDROut)
async def cidrs(cidr: schemas.NewCIDR, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        table = db.Table(f'{settings.cidr_table}')
        response = table.put_item(
        Item = { 
            'shrt_name': cidr.shrt_name,
            'description': cidr.description,
            'cidr': cidr.cidr,
            'next_available_ip': f'{ip(cidr.cidr)[0]}', 
            'total_available_ips' : ip(cidr.cidr).num_addresses
            }
        )
        return { 'cidr_created': True }
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail={ 'cidr_created': False })

@router.get('/cidrs', response_model=List[schemas.GetAllCIDRs])
async def cidrs(credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        table = db.Table(f'{settings.cidr_table}')
        response = table.scan()
        return (response['Items'])
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials")

@router.get('/cidrs/{shrt_name}', response_model=schemas.GetAllCIDRs)
async def get_cidr(shrt_name: str, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        table = db.Table(f'{settings.cidr_table}')
        response = table.get_item(Key={'shrt_name': shrt_name})
        if 'Item' in response:
            return (response['Item'])
        else: 
            raise HTTPException(status.HTTP_404_NOT_FOUND,
            detail="Not Found")
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials")
        print(response['Item'])
