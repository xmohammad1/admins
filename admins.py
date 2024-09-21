import asyncio
import aiohttp
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace with your actual Marzban panel URL
MARZBAN_URL = 'https://www.panel.org:2096'

# Replace with your actual Telegram bot token
TELEGRAM_BOT_TOKEN = '6223909608:AAHCdLkw5Ooz1MZSpG90Klkla9iy9uR1vFI'

async def get_access_token(username, password, url):
    """Get an access token from the Marzban panel asynchronously."""
    login_url = f'{url}/api/admin/token/'
    data = {
        'username': username,
        'password': password
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, data=data) as response:
            if response.status == 200:
                result = await response.json()
                return result['access_token']
            else:
                text = await response.text()
                raise Exception(f'Could not obtain token: {text}')

async def get_user_info(token, url, username):
    """Get user info from the Marzban panel using username asynchronously."""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    user_info_url = f'{url}/api/user/{username}'
    async with aiohttp.ClientSession() as session:
        async with session.get(user_info_url, headers=headers) as response:
            if response.status == 200:
                user_info = await response.json()
                return user_info
            else:
                text = await response.text()
                raise Exception(f'Could not obtain user info for {username}: {text}')

async def reset_usage(token, url, username):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    reset_url = f'{url}/api/user/{username}/reset'
    async with aiohttp.ClientSession() as session:
        async with session.post(reset_url, headers=headers) as response:
            if response.status == 200:
                return True
            else:
                text = await response.text()
                raise Exception(f'Could not reset usage for {username}: {text}')

async def revoke_subscription(token, url, username):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    revoke_url = f'{url}/api/user/{username}/revoke_sub'
    data = {}  # Include any required data here
    async with aiohttp.ClientSession() as session:
        async with session.post(revoke_url, headers=headers, json=data) as response:
            if response.status == 200:
                return True
            else:
                text = await response.text()
                raise Exception(f'Could not revoke subscription for {username}: {text}')

async def get_users(token, url, offset=0, limit=10):
    headers = {'Authorization': f'Bearer {token}'}
    users_url = f'{url}/api/users'
    params = {'offset': offset, 'limit': limit}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(users_url, headers=headers, params=params) as response:
            if response.status == 200:
                result = await response.json(content_type=None)
                # Ensure that result is a dictionary
                if isinstance(result, dict):
                    # Check if 'users' and 'total' keys are in the result
                    if 'users' in result and 'total' in result:
                        return result
                    else:
                        # If result is not as expected, handle accordingly
                        raise Exception(f'Unexpected response format: {result}')
                else:
                    raise Exception(f'Expected a dictionary but got {type(result)}')
            else:
                text = await response.text()
                raise Exception(f'Could not obtain users: {text}')

def time_since_last_active(online_at):
    if not online_at:
        return "N/A"

    # Parse the online_at timestamp into a datetime object
    last_active_time = datetime.strptime(online_at, '%Y-%m-%dT%H:%M:%S')

    # Calculate the time difference from now
    now = datetime.now()
    time_diff = now - last_active_time

    # Convert time difference to a human-readable format
    if time_diff < timedelta(minutes=1):
        return "Online"
    elif time_diff < timedelta(hours=1):
        minutes = int(time_diff.total_seconds() // 60)
        return f"{minutes} minute(s) ago"
    elif time_diff < timedelta(days=1):
        hours = int(time_diff.total_seconds() // 3600)
        return f"{hours} hour(s) ago"
    else:
        days = time_diff.days
        return f"{days} day(s) ago"

def convert_bytes_to_gb(bytes_value):
    return round(bytes_value / (1024 ** 3), 2)

def convert_bytes_to_mb(bytes_value):
    return round(bytes_value / (1024 ** 2), 2)

def get_days_until_expiration(expire_timestamp):
    if not expire_timestamp or expire_timestamp == 0:
        return "No expiration"

    try:
        expire_date = datetime.utcfromtimestamp(expire_timestamp)
    except (OSError, ValueError):
        return "Invalid date"

    now = datetime.utcnow()
    delta = expire_date - now
    if delta.days < 0:
        return "Expired"
    else:
        return f"{delta.days} day(s)"

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Define states
class Form(StatesGroup):
    username = State()
    password = State()
    menu = State()
    get_user_info_username = State()

# Start command handler
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Please enter your username:")
    await state.set_state(Form.username)

# Username handler
@dp.message(Form.username)
async def process_username(message: types.Message, state: FSMContext):
    await state.update_data(login_username=message.text)
    await message.answer("Please enter your password:")
    await state.set_state(Form.password)

# Password handler
@dp.message(Form.password)
async def process_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    login_username = user_data.get('login_username')
    password = message.text

    # Try to get the access token
    try:
        token = await get_access_token(login_username, password, MARZBAN_URL)
        await state.update_data(token=token)
        await message.answer("Login successful!", reply_markup=types.ReplyKeyboardRemove())
        # Show keyboard buttons to get user info and show users
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Get User Info"), types.KeyboardButton(text="Show Users")]],
            resize_keyboard=True
        )
        await message.answer("Choose an option:", reply_markup=keyboard)
        await state.set_state(Form.menu)
    except Exception as e:
        await message.answer(f"Login failed: {str(e)}")
        await state.clear()

# Menu handler
@dp.message(Form.menu)
async def process_menu(message: types.Message, state: FSMContext):
    if message.text == "Get User Info":
        await message.answer("Please enter the username you want to get info for:")
        await state.set_state(Form.get_user_info_username)
    elif message.text == "Show Users":
        # Get token from state
        user_data = await state.get_data()
        token = user_data.get('token')
        if token:
            try:
                offset = 0
                limit = 10
                users_result = await get_users(token, MARZBAN_URL, offset=offset, limit=limit)
                total_users = users_result.get('total', 0)
                users_list = users_result.get('users', [])

                # Save pagination info in state
                await state.update_data(users_offset=offset, users_limit=limit, total_users=total_users)
                # Display users
                await send_users_list(message, users_list, offset, limit, total_users)
            except Exception as e:
                await message.answer(f"Failed to get users: {str(e)}")
        else:
            await message.answer("Session expired. Please log in again.")
            await state.clear()
    else:
        await message.answer("Please use the provided options.")

# Handler to get the username for user info
@dp.message(Form.get_user_info_username)
async def process_get_user_info_username(message: types.Message, state: FSMContext):
    target_username = message.text
    user_data = await state.get_data()
    token = user_data.get('token')
    if token:
        try:
            user_status = await get_user_info(token, MARZBAN_URL, target_username)
            # Process and format the user status
            status_message = format_user_status(user_status)

            # Create inline keyboard with two buttons
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Reset Usage",
                        callback_data=f"reset_usage:{target_username}"
                    ),
                    InlineKeyboardButton(
                        text="Revoke Subscription",
                        callback_data=f"revoke_sub:{target_username}"
                    )
                ]
            ])

            # Send the status message with the inline keyboard
            await message.answer(status_message, reply_markup=keyboard)

            # After getting the info, go back to the menu state
            await state.set_state(Form.menu)
        except Exception as e:
            await message.answer(f"Failed to get user info: {str(e)}")
            # Optionally, go back to the menu
            await state.set_state(Form.menu)
    else:
        await message.answer("Session expired. Please log in again.")
        await state.clear()

def format_user_status(user_status):
    # Access data directly from user_status based on actual keys
    username = user_status.get('username', 'N/A')
    status = user_status.get('status', 'N/A')
    used_traffic_bytes = user_status.get('used_traffic', 0)
    data_limit_bytes = user_status.get('data_limit', None)
    expire_timestamp = user_status.get('expire', None)
    online_at = user_status.get('online_at', None)
    last_user_agent = user_status.get('sub_last_user_agent', 'N/A')

    # Convert used traffic and data limit from bytes to GB
    used_traffic_gb = convert_bytes_to_gb(used_traffic_bytes)

    # Safely handle the case where data_limit might be None or zero
    if data_limit_bytes is None or data_limit_bytes == 0:
        data_limit_gb = None
    else:
        data_limit_gb = convert_bytes_to_gb(data_limit_bytes)

    # Handle used traffic display (in MB if less than 1 GB)
    if used_traffic_gb < 1:
        used_traffic_mb = convert_bytes_to_mb(used_traffic_bytes)
        used_traffic_display = f"{used_traffic_mb} MB"
    else:
        used_traffic_display = f"{used_traffic_gb} GB"

    # Handle data limit display ("Unlimited" if None)
    if data_limit_gb is None:
        data_limit_display = "Unlimited"
    else:
        data_limit_display = f"{data_limit_gb} GB"

    # Calculate days until expiration
    days_until_expire = get_days_until_expiration(expire_timestamp)

    # Get the last active time and format it
    last_active_display = time_since_last_active(online_at)

    # Format and display the user's status
    status_message = (
        f"Username: {username}\n"
        f"Status: {status}\n"
        f"Expiration in: {days_until_expire}\n"
        f"Data Limit: {data_limit_display}\n"
        f"Used Traffic: {used_traffic_display}\n"
        f"Last Active: {last_active_display}\n"
        f"Last User Agent: {last_user_agent}\n"
    )
    return status_message

@dp.callback_query(lambda c: c.data and c.data.startswith('reset_usage:'))
async def process_reset_usage(callback_query: types.CallbackQuery, state: FSMContext):
    # Extract username from callback_data
    target_username = callback_query.data[len('reset_usage:'):]
    # Get token from state
    user_data = await state.get_data()
    token = user_data.get('token')
    if token:
        # Call the reset usage API endpoint
        try:
            await reset_usage(token, MARZBAN_URL, target_username)
            await callback_query.answer("Usage reset successfully.", show_alert=True)
        except Exception as e:
            await callback_query.answer(f"Failed to reset usage: {str(e)}", show_alert=True)
    else:
        await callback_query.answer("Session expired. Please log in again.", show_alert=False)

@dp.callback_query(lambda c: c.data and c.data.startswith('revoke_sub:'))
async def process_revoke_subscription(callback_query: types.CallbackQuery, state: FSMContext):
    # Extract username from callback_data
    target_username = callback_query.data[len('revoke_sub:'):]
    # Get token from state
    user_data = await state.get_data()
    token = user_data.get('token')
    if token:
        # Call the revoke subscription API endpoint
        try:
            await revoke_subscription(token, MARZBAN_URL, target_username)
            await callback_query.answer("Subscription revoked successfully.", show_alert=True)
        except Exception as e:
            await callback_query.answer(f"Failed to revoke subscription: {str(e)}", show_alert=True)
    else:
        await callback_query.answer("Session expired. Please log in again.", show_alert=False)

async def send_users_list(message, users_list, offset, limit, total_users):
    """Send a paginated list of users as InlineKeyboardButtons."""
    if not users_list:
        await message.answer("No users found.")
        return

    keyboard = build_users_keyboard(users_list, offset, limit, total_users)
    await message.answer("Select a user:", reply_markup=keyboard)

async def send_users_list_edit(message, users_list, offset, limit, total_users):
    """Edit the message to display a new list of users."""
    if not users_list:
        await message.edit_text("No users found.")
        return

    keyboard = build_users_keyboard(users_list, offset, limit, total_users)
    await message.edit_text("Select a user:", reply_markup=keyboard)

def build_users_keyboard(users_list, offset, limit, total_users):
    """Build the inline keyboard for the list of users."""
    keyboard_buttons = []
    for user in users_list:
        username = user.get('username', 'N/A')
        keyboard_buttons.append([InlineKeyboardButton(
            text=username,
            callback_data=f"user_detail:{username}"
        )])

    # Add pagination buttons if needed
    navigation_buttons = []
    if offset > 0:
        prev_offset = max(offset - limit, 0)
        navigation_buttons.append(InlineKeyboardButton(
            text="Previous Page",
            callback_data=f"users_page:{prev_offset}"
        ))
    if offset + limit < total_users:
        next_offset = offset + limit
        navigation_buttons.append(InlineKeyboardButton(
            text="Next Page",
            callback_data=f"users_page:{next_offset}"
        ))
    if navigation_buttons:
        keyboard_buttons.append(navigation_buttons)

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard

@dp.callback_query(lambda c: c.data and c.data.startswith('users_page:'))
async def process_users_page(callback_query: types.CallbackQuery, state: FSMContext):
    # Get new offset from callback_data
    offset_str = callback_query.data[len('users_page:'):]
    offset = int(offset_str)
    # Get token and limit from state
    user_data = await state.get_data()
    token = user_data.get('token')
    limit = user_data.get('users_limit', 10)
    total_users = user_data.get('total_users', 0)
    if token:
        try:
            users_result = await get_users(token, MARZBAN_URL, offset=offset, limit=limit)
            total_users = users_result.get('total', 0)
            users_list = users_result.get('users', [])

            # Update pagination info in state
            await state.update_data(users_offset=offset, total_users=total_users)
            # Edit the message with the new users list
            await send_users_list_edit(callback_query.message, users_list, offset, limit, total_users)
            await callback_query.answer()
        except Exception as e:
            await callback_query.answer(f"Failed to get users: {str(e)}", show_alert=True)
    else:
        await callback_query.answer("Session expired. Please log in again.", show_alert=False)

@dp.callback_query(lambda c: c.data and c.data.startswith('user_detail:'))
async def process_user_detail(callback_query: types.CallbackQuery, state: FSMContext):
    username = callback_query.data[len('user_detail:'):]
    # Get token from state
    user_data = await state.get_data()
    token = user_data.get('token')
    offset = user_data.get('users_offset', 0)
    limit = user_data.get('users_limit', 10)
    total_users = user_data.get('total_users', 0)
    if token:
        try:
            # Get user info and display
            user_status = await get_user_info(token, MARZBAN_URL, username)
            status_message = format_user_status(user_status)
            # Create "Back" button
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Back to Users List",
                        callback_data=f"users_page:{offset}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Reset Usage",
                        callback_data=f"reset_usage:{username}"
                    ),
                    InlineKeyboardButton(
                        text="Revoke Subscription",
                        callback_data=f"revoke_sub:{username}"
                    )
                ]
            ])
            await callback_query.message.edit_text(status_message, reply_markup=keyboard)
            await callback_query.answer()
        except Exception as e:
            await callback_query.answer(f"Failed to get user info: {str(e)}", show_alert=True)
    else:
        await callback_query.answer("Session expired. Please log in again.", show_alert=False)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
