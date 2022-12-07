import os
from datetime import datetime
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
async def new_ntwrks(new_ntwrk: schemas.NewNetwork, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    if (' ' in new_ntwrk.shrt_name) == True:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
        detail=f"{new_ntwrk.shrt_name} should be a contiguous string.")
    else:
        jwt_user = cognito.validate_user_id(
            token = credentials.credentials, 
            region = f'{settings.region_name}', 
            idp_pool = os.environ.get('COGNITO_POOL_ID'), 
            client_id = os.environ.get('APP_CLIENT_ID')
        )
        print(jwt_user['user_verified'])
        if jwt_user['user_verified']:
            print(jwt_user['user_verified'])
            ddb_table = db.Table(f'{settings.ddb_table}')
            ddb_resp = ddb_table.get_item(Key={'shrt_name': new_ntwrk.shrt_name})
            if 'Item' in ddb_resp:
                raise HTTPException(status.HTTP_409_CONFLICT,
                detail=f"{new_ntwrk.shrt_name} Already Exists")
            cidr_table = db.Table(f'{settings.cidr_table}')
            cidr_resp = cidr_table.get_item(Key={'shrt_name': new_ntwrk.cidr_name})
            if 'Item' in cidr_resp:
                network = '%s%s%s' %(cidr_resp['Item']['next_available_ip'], str("/"), new_ntwrk.subnet_mask)
                new_ntwrk_resp = ddb_table.put_item(
                    Item = { 
                    'shrt_name': new_ntwrk.shrt_name,
                    'description': new_ntwrk.description,
                    'network': network,
                    'total_ips' : ip(network).num_addresses,
                    'in_use' : new_ntwrk.in_use,
                    'Information': new_ntwrk.meta_data,
                    'ntwrk_id': new_ntwrk.ntwrk_id,
                    'date': datetime.now().strftime("%Y-%m-%d")
                    }
                )
                cidr_update_resp = cidr_table.put_item(
                    Item = { 
                        'shrt_name': cidr_resp['Item']['shrt_name'],
                        'description': cidr_resp['Item']['description'],
                        'cidr': cidr_resp['Item']['cidr'],
                        'next_available_ip': f'{ip(network)[-1] + 1}', 
                        'total_available_ips' : cidr_resp['Item']['total_available_ips'] - ip(network).num_addresses,
                        'in_use': True,
                        'reclaimed_networks': cidr_resp['Item']['reclaimed_networks']
                        }
                    )
                return { 'shrt_name': new_ntwrk.shrt_name,'network': network }
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
            detail={ 'cidr_created': False })

@router.post('/networks/reclaim', status_code=status.HTTP_201_CREATED, response_model=schemas.NewNetworkOut)
async def reclaim_ntwrk(new_ntwrk: schemas.ReclaimNetwork, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        cidr_table = db.Table(f'{settings.cidr_table}')
        ddb_table = db.Table(f'{settings.ddb_table}')
        cidr_resp = cidr_table.get_item(Key={'shrt_name': new_ntwrk.cidr_name})
        ddb_resp = cidr_table.get_item(Key={'shrt_name': new_ntwrk.shrt_name})
        reclaimed_networks = cidr_resp['Item']['reclaimed_networks']
        if 'Item' in ddb_resp:
            raise HTTPException(status.HTTP_409_CONFLICT,
            detail=f"{new_ntwrk.shrt_name} Already Exists")
        if 'Item' in cidr_resp:
            if new_ntwrk.ntwrk_cidr in cidr_resp['Item']['reclaimed_networks']:
                new_ntwrk_resp = ddb_table.put_item(
                    Item = { 
                    'shrt_name': new_ntwrk.shrt_name,
                    'description': new_ntwrk.description,
                    'network': new_ntwrk.ntwrk_cidr,
                    'total_ips' : ip(new_ntwrk.ntwrk_cidr).num_addresses,
                    'in_use' : new_ntwrk.in_use,
                    'Information': new_ntwrk.meta_data,
                    'ntwrk_id': new_ntwrk.ntwrk_id,
                    'date': datetime.now().strftime("%Y-%m-%d")
                    }
                )
                reclaimed_networks = reclaimed_networks.remove(new_ntwrk.ntwrk_cidr)
                cidr_update_resp = cidr_table.put_item(
                    Item = { 
                        'shrt_name': cidr_resp['Item']['shrt_name'],
                        'description': cidr_resp['Item']['description'],
                        'cidr': cidr_resp['Item']['cidr'],
                        'next_available_ip': cidr_resp['Item']['next_available_ip'], 
                        'total_available_ips' : cidr_resp['Item']['total_available_ips'] - ip(new_ntwrk.ntwrk_cidr).num_addresses,
                        'in_use': True,
                        'reclaimed_networks': reclaimed_networks 
                        }
                    )
                return { 'shrt_name': new_ntwrk.shrt_name,'network': new_ntwrk.ntwrk_cidr }
        else: 
            raise HTTPException(status.HTTP_404_NOT_FOUND,
            detail="CIDR {cidr_name} Not Found")
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail={ 'cidr_created': False })

@router.put('/networks/{shrt_name}', response_model=schemas.UpdateNetworkOut)
async def update_cidr(shrt_name: str, network: schemas.UpdateNetwork, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        ddb_table = db.Table(f'{settings.ddb_table}')
        ddb_resp = ddb_table.get_item(Key={'shrt_name': shrt_name})
        if 'Item' in ddb_resp:
            new_ntwrk_resp = ddb_table.put_item(
                    Item = { 
                    'shrt_name': ddb_resp['Item']['shrt_name'],
                    'description': ddb_resp['Item']['description'],
                    'network': ddb_resp['Item']['network'],
                    'total_ips' : ddb_resp['Item']['total_ips'],
                    'in_use' : network.in_use,
                    'Information': network.meta_data,
                    'ntwrk_id': network.ntwrk_id,
                    'date': datetime.now().strftime("%Y-%m-%d")
                    }
                )
            return { 'network_updated': True }
        else: 
            raise HTTPException(status.HTTP_404_NOT_FOUND,
            detail="Not Found")
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials")

@router.get('/networks/{shrt_name}', response_model=schemas.GetAllNetworks)
async def get_cidr(shrt_name: str, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        table = db.Table(f'{settings.ddb_table}')
        response = table.get_item(Key={'shrt_name': shrt_name})
        if 'Item' in response:
            return (response['Item'])
        else: 
            raise HTTPException(status.HTTP_404_NOT_FOUND,
            detail="Not Found")
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials")

@router.get('/networks', response_model=List[schemas.GetAllNetworks])
async def cidrs(credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        table = db.Table(f'{settings.ddb_table}')
        response = table.scan()
        return (response['Items'])

    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials")

@router.delete('/networks', status_code=status.HTTP_204_NO_CONTENT)
async def del_network(shrt_name: str, cidr_name: str, credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    jwt_user = cognito.validate_user_id(
        token = credentials.credentials, 
        region = f'{settings.region_name}', 
        idp_pool = os.environ.get('COGNITO_POOL_ID'), 
        client_id = os.environ.get('APP_CLIENT_ID')
    )
    if jwt_user['user_verified']:
        table = db.Table(f'{settings.ddb_table}')
        cidr_table = db.Table(f'{settings.cidr_table}')
        cidr_resp = cidr_table.get_item(Key={'shrt_name': cidr_name})
        get_item = table.get_item(
            Key = 
                {
                    'shrt_name': shrt_name
                }
            )
        if 'Item' in get_item:
            if get_item['Item']['in_use']:
                raise HTTPException(status.HTTP_412_PRECONDITION_FAILED,
                detail=f"CIDR {shrt_name} is in use - CANNOT DELETE.")
            else:
                reclaimed_networks = cidr_resp['Item']['reclaimed_networks']
                if reclaimed_networks is None:
                     reclaimed_networks = []
                reclaimed_networks.append(get_item['Item']['network'])
                del_item = table.delete_item(
                    Key = 
                        {
                            'shrt_name': shrt_name
                        }
                    )
                
                cidr_update_resp = cidr_table.put_item(
                    Item = { 
                            'shrt_name': cidr_resp['Item']['shrt_name'],
                            'description': cidr_resp['Item']['description'],
                            'cidr': cidr_resp['Item']['cidr'],
                            'next_available_ip': cidr_resp['Item']['next_available_ip'], 
                            'total_available_ips' : cidr_resp['Item']['total_available_ips'] + get_item['Item']['total_ips'],
                            'in_use': cidr_resp['Item']['in_use'],
                            'reclaimed_networks': reclaimed_networks
                        }
                    )
                return Response(status_code=status.HTTP_204_NO_CONTENT)
        else: 
            raise HTTPException(status.HTTP_404_NOT_FOUND,
            detail="Not Found")
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials")
