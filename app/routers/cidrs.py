import os
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
    try:
        jwt_user = cognito.validate_user_id(
            token = credentials.credentials, 
            region = f'{settings.region_name}', 
            idp_pool = os.environ.get('COGNITO_POOL_ID'), 
            client_id = os.environ.get('APP_CLIENT_ID')
        )
        print(jwt_user)
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
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
            detail=f"Please re-authenticate.")
        return { 'cidr_created': True }
    except Exception as e:
        print(e)

@router.get('/cidrs')
async def cidrs(credentials: HTTPAuthorizationCredentials= Depends(security), db: Session = Depends(db.initialize_db)):
    table = db.Table(f'{settings.cidr_table}')
    response = table.put_item(
    Item = { 
        'shrt_name': 'Kelvin Galabuzi',
        'Email': 'kelvingalabuzi@handson.cloud'
        }
    )
    print(response)
    # print(credentials.credentials)
    # return (credentials.credentials)
