from models.user import UserStatus, UserResponse
from datetime import datetime
from utils.lang import MessageTexts
from io import BytesIO
import qrcode
from jdatetime import datetime as jdtime


def humanize_time_difference(target_time: datetime, reference_time: datetime = None) -> str:
    if not reference_time:
        reference_time = datetime.utcnow()

    delta = target_time - reference_time
    total_seconds = int(delta.total_seconds())
    days, remainder = divmod(abs(total_seconds), 86400)  
    
    if total_seconds >= 0:
        return f"{days}" if days > 0 else "➖"
    else:
        return f"{days}" if days > 0 else "➖"

async def user_account_text(user: UserResponse, is_test: bool = False) -> str:
    now = datetime.utcnow()

    expire_str = '♾️' if not user.expire or user.expire != 0 else humanize_time_difference(datetime.fromtimestamp(user.expire), now)
    created_at_str = humanize_time_difference(user.created_at, now)
    on_hold_timeout_str = humanize_time_difference(user.on_hold_timeout, now) if user.on_hold_timeout else "➖"
    online_at_str = humanize_time_difference(user.online_at, now) if user.online_at else "➖"
    formatted_links = "\n\n".join([f"🔗 {link}" for link in user.links])

    common_fields = {
        "username": user.username,
        "status": user.status,
        "expire": expire_str,
        "data_limit": round(user.data_limit / 1073741824, 3) if user.data_limit != 0 else '♾️',
        "data_limit_reset_strategy": user.data_limit_reset_strategy,
        "used_traffic": round(user.used_traffic / 1073741824, 3) if user.data_limit != 0 else '➖',
        "lifetime_used_traffic": round(user.lifetime_used_traffic / 1073741824, 3) if user.data_limit != 0 else '➖' ,
        "created_at": created_at_str,
        "subscription_url": user.subscription_url,
        "admin": user.admin.username if user.admin else "➖",
        "note": user.note or "➖",
        "on_hold_timeout": on_hold_timeout_str,
        "on_hold_expire_duration": f"{user.on_hold_expire_duration // 86400} days" if user.on_hold_expire_duration else "➖",
        "online_at": online_at_str,
        "links" : formatted_links,
        "today" : jdtime.utcnow()
    }

    if user.status == UserStatus.On_hold:
        return MessageTexts.UserOnHoldResponse.format(**common_fields)
    else:
        return MessageTexts.UserActiveResponse.format(**common_fields)


async def create_qr(text: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=7,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="transparent").convert("RGBA")    
    img_bytes_io = BytesIO()
    qr_img.save(img_bytes_io, 'PNG')
    return img_bytes_io.getvalue()