import os
from datetime import datetime
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..IdpSetup import PoolExists, validate_client_id
from ..models import does_table_exist
from ..config import settings
from .. import schemas, db

router = APIRouter(
    tags=['Health']
    )
ddb = db.initialize_db()

@router.get('/health', response_model=schemas.HealthPage)
async def health(response: Response):
    cidr_table = does_table_exist(ddb, f'{settings.cidr_table}')
    ddb_table = does_table_exist(ddb, f'{settings.ddb_table}')
    idp = PoolExists()
    client_details = validate_client_id(os.environ.get('COGNITO_POOL_ID'), os.environ.get('APP_CLIENT_ID'))
    if cidr_table['table_exists'] and ddb_table['table_exists'] and idp['identity_setup_valid']:
        return(
            {
                'name': "Ntwrk_Calc_API",
                'subsystems': [
                    {
                        f'{settings.cidr_table}': cidr_table,
                        f'{settings.ddb_table}': ddb_table,
                        'Identity': [
                                idp,
                                client_details
                            ]
                    }
                ],
                'date': datetime.now(),
                'status': 'Good'
            }
        )
    else:
        response.status_code=status.HTTP_417_EXPECTATION_FAILED
        return(
            {
                'name': "Ntwrk_Calc_API",
                'subsystems': [
                    {
                        f'{settings.cidr_table}': cidr_table,
                        f'{settings.ddb_table}': ddb_table,
                        'Identity': [
                                idp,
                                client_details
                            ]
                    }
                ],
                'date': datetime.now(),
                'status': 'Check Dependencies'
            }
        )
