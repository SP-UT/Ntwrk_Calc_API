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

@router.post('/batch/networks', status_code=status.HTTP_201_CREATED, response_model=List[schemas.NewNetworkOut])
async def new_ntwrks(new_ntwrk: schemas.BatchNewNetwork, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        table = db.Table(f'{settings.ddb_table}')
        response = table.scan()
        li_shrt= []
        resp_ntwrks = []
        for item in response['Items']:
            li_shrt.append(item['shrt_name'])
        print(li_shrt)
        cidr_table = db.Table(f'{settings.cidr_table}')
        cidr_resp = cidr_table.get_item(Key={'shrt_name': new_ntwrk.cidr_name})
        total_cidr_ips = cidr_resp['Item']['total_available_ips']
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
                next_ip = f'{ip(net)[-1] + 1}'
                total_cidr_ips = total_cidr_ips - ip(net).num_addresses
                new_ntwrk_resp = table.put_item(
                    Item = { 
                    'shrt_name': netwrk.shrt_name,
                    'description': netwrk.description,
                    'network': net,
                    'total_ips' : ip(net).num_addresses,
                    'in_use' : netwrk.in_use,
                    'Information': netwrk.meta_data,
                    'ntwrk_id': netwrk.ntwrk_id,
                    'date': datetime.now().strftime("%Y-%m-%d")
                    }
                )
                resp_ntwrks.append({'shrt_name': netwrk.shrt_name, 'network': net})
        cidr_update_resp = cidr_table.put_item(
            Item = { 
                'shrt_name': cidr_resp['Item']['shrt_name'],
                'description': cidr_resp['Item']['description'],
                'cidr': cidr_resp['Item']['cidr'],
                'next_available_ip': next_ip, 
                'total_available_ips' : total_cidr_ips,
                'in_use': True,
                'reclaimed_networks': cidr_resp['Item']['reclaimed_networks']
                }
        )
        return (resp_ntwrks)
                # print(net)
                # print(next_ip)
                # print(netwrk)
                # print(date)
                # print(total_ips)
                # print(total_cidr_ips)
