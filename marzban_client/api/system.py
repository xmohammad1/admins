from ..request import req
from models.system import ProxyInbounds

class System:
    def __init__(self, username: str, password: str, address: str) -> None:
        self.username = username
        self.password = password
        self.address = address
    
    async def inbounds(self) -> dict:
        """
        Get inbounds data
        """
        return await req(
            endpoint='/inbounds',
            response_model=ProxyInbounds
        )
