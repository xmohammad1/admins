from ..request import req
from models.user import UserCreate, UserModify, UserResponse, UsersResponse

class User:
    def __init__(self, username: str, password: str, address: str) -> None:
        self.username = username
        self.password = password
        self.address = address
    
    async def get(self, username: str) -> dict:
        """
        Get a user info from Marzban panel with username.
        """
        return await req(
            endpoint=f'/user/{username}',
            response_model=UserResponse
        )
    
    async def edit(self, username: str, data: UserModify) -> dict:
        """
        Edit a user data from Marzban panel with username and UserModify data.
        """
        return await req(
            endpoint=f'/user/{username}',
            method='PUT',
            data=data.dict(),
            response_model=UserResponse
        )
    
    async def add(self, user_data: UserCreate) -> UserResponse:
        """
        Add a new user to Marzban panel using UserCreate model.
        """
        response = await req(
            endpoint='/user',
            method='POST',
            data=user_data.dict(),
            response_model=UserResponse
        )
        return response
    
    async def all(self) -> dict:
        """
        Get all users from Marzban panel.
        """
        return await req(
            endpoint='/users',
            response_model=UsersResponse
        )

    async def reset_data_usage(self, username: str) -> bool:
        """
        Reset a user's data usage.
        """
        return await req(
            endpoint=f'/user/{username}/reset'
        )

    async def delete(self, username: str) -> bool:
        """
        Delete a user from Marzban panel.
        """
        return await req(
            endpoint=f'/user/{username}',
            method='DELETE'
        )
