from pydantic import BaseModel
from enum import Enum
from typing import Union, List

class ProxyTypes(str, Enum):
    VMess = "vmess"
    VLESS = "vless"
    Trojan = "trojan"
    Shadowsocks = "shadowsocks"

class ProxyInboundConfig(BaseModel):
    tag: str
    protocol: ProxyTypes
    network: str
    tls: str
    port: Union[int, str]

class ProxyInbounds(BaseModel):
    vless: List[ProxyInboundConfig]
    vmess: List[ProxyInboundConfig] = []
    trojan: List[ProxyInboundConfig] = []
    shadowsocks: List[ProxyInboundConfig] = []

    @property
    def all_inbounds(self) -> List[ProxyInboundConfig]:
        return self.vless + self.vmess + self.trojan + self.shadowsocks