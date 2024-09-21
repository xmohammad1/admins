from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional
from .admin import Admin
from pydantic import BaseModel

class UserStatus(str, Enum):
    Active = "active"
    Disabled = "disabled"
    Limited = "limited"
    Expired = "expired"
    On_hold = "on_hold"

class UserDataLimitResetStrategy(str, Enum):
    No_reset = "no_reset"
    Day = "day"
    Week = "week"
    Month = "month"
    Year = "year"

class UserResponse(BaseModel):
    username: str
    status: str
    expire: Optional[int] 
    data_limit: Optional[int]
    data_limit_reset_strategy: str  
    used_traffic: int
    lifetime_used_traffic: int
    created_at: datetime
    links: List[str]  
    subscription_url: str
    proxies: Dict[str, dict]
    excluded_inbounds: Dict[str, List[str]]
    admin: Optional['Admin'] 
    note: Optional[str] 
    on_hold_timeout: Optional[datetime] 
    on_hold_expire_duration: Optional[int] = 0 
    auto_delete_in_days: Optional[int] 
    online_at: Optional[datetime] 
    sub_updated_at: Optional[datetime] = None  
    sub_last_user_agent: Optional[str] = ""  
    inbounds: Dict[str, List[str]]

class UserCreate(BaseModel):
    username: str
    proxies: Dict[str, dict]
    inbounds: Dict[str, List[str]] 
    expire: Optional[int] = None
    data_limit: Optional[int] = None
    data_limit_reset_strategy: UserDataLimitResetStrategy = None
    status: UserStatus = UserStatus.Active
    note: Optional[str] = None
    on_hold_timeout: Optional[str] = None
    on_hold_expire_duration: Optional[int] = 0

class UserModify(BaseModel):
    proxies: Dict[str, dict] = None
    inbounds: Dict[str, List[str]] = None
    expire: Optional[int] = None
    data_limit: Optional[int] = None
    data_limit_reset_strategy: UserDataLimitResetStrategy = None
    status: UserStatus = None
    note: Optional[str] = None
    on_hold_timeout: Optional[str] = None
    on_hold_expire_duration: Optional[int] = None

class UsersResponse(BaseModel):
    users: List[UserResponse]
    total: int

class UserType(str, Enum):
    Test = 'test'
    Marz = 'marz'