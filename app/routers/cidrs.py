import os
from typing import List
from ipaddress import IPv4Network as ip
from fastapi import status, HTTPException, Depends, APIRouter, Response
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
        cidr_resp = table.get_item(Key={'shrt_name': cidr.shrt_name})
        if 'Item' in cidr_resp:
            raise HTTPException(status.HTTP_409_CONFLICT,
            detail=f"{cidr.shrt_name} Already Exists")
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

@router.put('/cidrs/{shrt_name}', response_model=schemas.UpdateCIDROut)
async def update_cidr(shrt_name: str, cidr: schemas.UpdateCIDR, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
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
            update_cidr = table.put_item(
                Item = { 
                    'shrt_name': cidr.shrt_name,
                    'description': cidr.description,
                    'cidr': response['Item']['cidr'],
                    'next_available_ip': response['Item']['next_available_ip'], 
                    'total_available_ips' : response['Item']['total_available_ips']
                    }
                )
            return({"cidr_updated": True})
        else: 
            raise HTTPException(status.HTTP_404_NOT_FOUND,
            detail="Not Found")
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials")

@router.delete('/cidrs/{shrt_name}', status_code=status.HTTP_204_NO_CONTENT)
async def del_cidr(shrt_name: str, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        table = db.Table(f'{settings.cidr_table}')
        get_item = table.get_item(
            Key = 
                {
                    'shrt_name': shrt_name
                }
            )
        if 'Item' in get_item:
            del_item = table.delete_item(
                Key = 
                    {
                        'shrt_name': shrt_name
                    }
                )
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else: 
            raise HTTPException(status.HTTP_404_NOT_FOUND,
            detail="Not Found")
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials")
