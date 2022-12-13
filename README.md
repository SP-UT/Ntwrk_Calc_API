# Ntwrk_Calc_API
 Network Address Space Mgmt API uses AWS Cognito for user authentication and AWS DynamoDB Tables as backend.

### Application Environment Setup

#### Python Version
```
python --version               
Python 3.10.1
```

#### Create / Activate Virtual Environment
```
python3 -m venv ntwrk_calc_api
source ntwrk_calc_api/bin/activate
```

#### Install PIP
```
python -m pip install --upgrade pip
```

#### Install Application Dependencies
```
pip install -r requirements.txt
```

#### Export Application Environment
```
export DDB_TABLE=[Default Table Name]
export CIDR_TABLE=[CIDR Table Name]
export REGION_NAME=[AWS REGION HERE]
export AWS_ACCESS_KEY=[AWS ACCESS KEY HERE]
export AWS_SECRET_ACCESS_KEY=[AWS SECRET ACCESS KEY HERE]
```
In `main.py` if `@app.on_event("startup")` Cognito Pool and Dynamo DB Table creation code is commented out - please export the below environment variables.
```
export COGNITO_POOL_ID=[COGNITO POOL ID HERE]
export APP_CLIENT_ID=[APP CLIENT ID HERE]
```

#### Setup Cognito IDP User Accounts
File Setup and Required Account Information
```
touch app/user_accts.csv
echo uname,email@email.com >> app/user_accts.csv
```
#### Cognito IDP Application Integration Secret
Network Client `Ntwrk_Calc_API` is created upon startup.
The Client ID is available as `APP_CLIENT_ID` environment variable upon successful application startup.

#### Cleanup
The `shutdown` event of FASTAPI will delete the `DDB_TABLE`, `CIDR_TABLE` and the Cognito IDP environment setup.
To ensure cleanup of resources - please uncomment the code in `@app.on_event("shutdown")` to delete resources in `main.py` file.

#### Start the API
```
uvicorn app.main:app --reload
```
