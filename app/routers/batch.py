import os
from fastapi import status, HTTPException, Depends, APIRouter, Response
from .. import db, schemas, cognito
from sqlalchemy.orm import Session
from ..config import settings
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime
from typing import List
from ipaddress import IPv4Network as ip

router = APIRouter(
    tags=['Batch']
    )

security = HTTPBearer()

@router.post('/batch/networks', status_code=status.HTTP_201_CREATED, response_model=schemas.NewNetworkOut)
async def new_ntwrks(new_ntwrk: schemas.BatchNewNetwork, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    create_ntwrks = new_ntwrk
    if jwt_user['user_verified']:
        table = db.Table(f'{settings.ddb_table}')
        response = table.scan()
        li_shrt = [] 
        for item in response['Items']:
            li_shrt.append(item['shrt_name'])
        print(li_shrt)
        cidr_table = db.Table(f'{settings.cidr_table}')
        cidr_resp = cidr_table.get_item(Key={'shrt_name': new_ntwrk.cidr_name})
        print(cidr_resp['Item'])
        next_ip = cidr_resp['Item']['next_available_ip']
        for netwrk in new_ntwrk.networks:
            if (' ' in netwrk.shrt_name) == True:
                raise HTTPException(status.HTTP_400_BAD_REQUEST,
                detail=f"{netwrk.shrt_name} should be a contiguous string.")
            elif netwrk.shrt_name in li_shrt:
                raise HTTPException(status.HTTP_409_CONFLICT,
                detail=f"{netwrk.shrt_name} Already Exists")
            else:  
                net = '%s%s%s' %(next_ip, str("/"), netwrk.subnet_mask) 
                #TypeError: 'BatchNetworkModel' object does not support item assignment 
                #netwrk['total_ips'] = ip(net).num_addresses
                #netwrk['date'] = datetime.now().strftime("%Y-%m-%d")
                next_ip = f'{ip(net)[-1] + 1}'
                print(netwrk)
                print(net)
                print(next_ip)
                print(create_ntwrks)
