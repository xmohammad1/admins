from .api.user import User
from .api.system import System
from .request import req

from utils.config import MARZBAN_USERNAME, MARZBAN_PASSWORD, MARZBAN_ADDRESS

class Panel:
    def __init__(self, username: str, password: str, address: str) -> None:
        self.user = User(
            username,
            password,
            address
        )
        self.system = System(
            username,
            password,
            address
        )

panel = Panel(
    MARZBAN_USERNAME,
    MARZBAN_PASSWORD,
    MARZBAN_ADDRESS
)