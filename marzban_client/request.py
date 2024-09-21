import httpx
from typing import Optional, Dict, Any, Type, TypeVar
from utils.log import logger
from utils.config import MARZBAN_ADDRESS
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

async def req(
    endpoint: str,
    token: str = '',
    method: str = 'GET',
    data: Optional[Dict[str, Any]] = None,
    response_model: Optional[Type[T]] = None
) -> Optional[T]:
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    if token:
        headers['Authorization'] = f"Bearer {token}"

    url = f'{MARZBAN_ADDRESS}/api{endpoint}'

    try:
        async with httpx.AsyncClient() as client:
            if method.upper() == 'GET':
                response = await client.get(url, params=data, headers=headers)
            elif method.upper() == 'POST':
                response = await client.post(url, json=data, headers=headers)
            else:
                response = await client.request(method, url, json=data, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            if response_model:
                return response_model.parse_obj(response_json)

            return response_json

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"An error occurred while making the request: {str(e)}")
    except ValueError as e:
        logger.error(f"Failed to decode JSON response: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        
    return None