from pydantic import BaseModel
from typing import List
from datetime import datetime

class HealthPage(BaseModel):
    name: str
    subsystems: List
    date: datetime
    status: str
    
class UserChangePassword(BaseModel):
    token: str
    password: str
    new_password: str

class ChangePasswordOut(BaseModel):
    password_changed: bool

class NewCIDROut(BaseModel):
    cidr_created: bool

class NewCIDR(BaseModel):
    shrt_name: str
    description: str
    cidr: str

class GetAllCIDRs(BaseModel):
    shrt_name: str
    description: str
    cidr: str
    next_available_ip: str
    total_available_ips: int

class UpdateCIDR(BaseModel):
    shrt_name: str
    description: str

class UpdateCIDROut(BaseModel):
    cidr_updated: bool

class UserOut(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    token_id: str

class NewNetwork(BaseModel):
    shrt_name: str
    cidr_name: str
    subnet_mask: int
    description: str

class NewNetworkOut(BaseModel):
    shrt_name: str
    network: str

class NetworkUsageStatus(BaseModel):
    in_use: bool
    ntwrk_id: str
    
