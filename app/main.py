import os, csv
from fastapi import FastAPI
from .db import initialize_db
from .models import generate_table, drop_table
from .idp import UserPoolSetup, DelPoolSetup, create_app_client, create_user


db = initialize_db()
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    generate_table()
    poolid = UserPoolSetup()
    client_id = create_app_client(poolid)
    os.environ['APP_CLIENT_ID'] = client_id
    with open("app/user_accts.csv", 'r') as file:
        csvr = csv.reader(file)
        for row in csvr:
            create_user(poolid, row[0], row[1])    

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("shutdown")
def shutdown_event():
    drop_table()
    DelPoolSetup()
