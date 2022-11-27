from pydantic import BaseSettings

class Settings(BaseSettings):
    ddb_table: str
    cidr_table: str
    auth_table: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str

    class Config:
        env_file = ".env"
        case_sensitive = True
        fields = {
            "ddb_table": {
                "env": "DDB_TABLE"
            },
            "cidr_table": {
                "env": "CIDR_TABLE"
            },
            "auth_table": {
                "env": "AUTH_TABLE"
            },
            "region_name": {
                "env": "REGION_NAME"
            },
            "aws_access_key_id": {
                "env": "AWS_ACCESS_KEY"
            },
            "aws_secret_access_key": {
                "env": "AWS_SECRET_ACCESS_KEY"
            }
        }

settings = Settings()
