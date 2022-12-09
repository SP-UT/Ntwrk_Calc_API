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
    tags=['Batch Networks']
    )

security = HTTPBearer()

@router.post('batch/networks', status_code=status.HTTP_201_CREATED, response_model=schemas.NewNetworkOut)
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
        if jwt_user['user_verified']:
            print(jwt_user['user_verified'])
