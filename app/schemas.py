from pydantic import BaseModel
from typing import List, Optional
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
    in_use: Optional[bool] = False
    reclaimed_networks: Optional[List] = None

class GetAllCIDRs(BaseModel):
    shrt_name: str
    description: str
    cidr: str
    next_available_ip: str
    total_available_ips: int
    reclaimed_networks: Optional[List] = []

class UpdateCIDR(BaseModel):
    description: Optional[str]
    in_use: Optional[bool]
    reclaimed_networks: Optional[List]

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
    in_use: Optional[bool]
    ntwrk_id: Optional[str]
    meta_data: Optional[str]

class NewNetworkOut(BaseModel):
    shrt_name: str
    network: str

class UpdateNetwork(BaseModel):
    in_use: Optional[bool]
    ntwrk_id: Optional[str]
    meta_data: Optional[str]

class UpdateNetworkOut(BaseModel):
    network_updated: bool

class GetAllNetworks(BaseModel):
    shrt_name: str
    date: str
    description: str
    total_ips: int
    Information: Optional[str]
    network: Optional[str]
    in_use: Optional[bool]
    ntwrk_id: Optional[str]
    meta_data: Optional[str]
