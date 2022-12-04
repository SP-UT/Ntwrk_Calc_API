import os, csv
from fastapi import FastAPI
from .db import initialize_db
from .routers import auth, cidrs, health, networks
from .models import generate_table, drop_table
from .IdpSetup import UserPoolSetup, DelPoolSetup, create_app_client, create_user


db = initialize_db()
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Startup now.")
    # generate_table()
    # poolid = UserPoolSetup()
    # client_id = create_app_client(poolid)
    # os.environ['COGNITO_POOL_ID'] = poolid
    # os.environ['APP_CLIENT_ID'] = client_id
    # with open("app/user_accts.csv", 'r') as file:
    #     csvr = csv.reader(file)
    #     for row in csvr:
    #         create_user(poolid, row[0], row[1])    

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(auth.router)
app.include_router(cidrs.router)
app.include_router(health.router)
app.include_router(networks.router)


@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down now.")
    # drop_table()
    # DelPoolSetup()
