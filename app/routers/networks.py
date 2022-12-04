import os
from typing import List
from ipaddress import IPv4Network as ip
from fastapi import status, HTTPException, Depends, APIRouter, Response
from .. import db, schemas, cognito
from sqlalchemy.orm import Session
from ..config import settings
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter(
    tags=['Networks']
    )

security = HTTPBearer()

@router.post('/networks', status_code=status.HTTP_201_CREATED, response_model=schemas.NewNetworkOut)
async def cidrs(new_ntwrk: schemas.NewNetwork, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        ddb_table = db.Table(f'{settings.ddb_table}')
        ddb_resp = ddb_table.get_item(Key={'shrt_name': new_ntwrk.shrt_name})
        if 'Item' in ddb_resp:
            raise HTTPException(status.HTTP_409_CONFLICT,
            detail=f"{new_ntwrk.shrt_name} Already Exists")
        cidr_table = db.Table(f'{settings.cidr_table}')
        cidr_resp = cidr_table.get_item(Key={'shrt_name': new_ntwrk.cidr_name})
        print(cidr_resp)
        if 'Item' in cidr_resp:
            network = '%s%s%s' %(cidr_resp['Item']['next_available_ip'], str("/"), new_ntwrk.subnet_mask)
            new_ntwrk_resp = ddb_table.put_item(
                Item = { 
                'shrt_name': new_ntwrk.shrt_name,
                'description': new_ntwrk.description,
                'network': network,
                'total_ips' : ip(network).num_addresses,
                'in_use' : False
                }
            )
            cidr_update_resp = cidr_table.put_item(
                Item = { 
                    'shrt_name': cidr_resp['Item']['shrt_name'],
                    'description': cidr_resp['Item']['description'],
                    'cidr': cidr_resp['Item']['cidr'],
                    'next_available_ip': f'{ip(network)[-1] + 1}', 
                    'total_available_ips' : cidr_resp['Item']['total_available_ips'] - ip(network).num_addresses
                    }
                )
            return { 'shrt_name': new_ntwrk.shrt_name,'network': network }
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
            detail={ 'cidr_created': False })
