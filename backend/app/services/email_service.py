from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import secrets

from app.core.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="app/templates",
)


def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


async def send_otp_email(
    email: str,
    name: str,
    otp: str,
):
    message = MessageSchema(
        subject="Email Verification OTP",
        recipients=[email],
        template_body={
            "name": name,
            "otp": otp,
        },
        subtype="html",
    )

    fm = FastMail(conf)

    await fm.send_message(
        message,
        template_name="email_verification.html",
    )


async def send_order_confirmation_email(
    email: str,
    name: str,
    order_id: int,
    order_date: str,
    payment_status: str,
    total_amount: float,
):
    message = MessageSchema(
        subject=f"Order #{order_id} Confirmed",
        recipients=[email],
        template_body={
            "name": name,
            "order_id": order_id,
            "order_date": order_date,
            "payment_status": payment_status,
            "total_amount": total_amount,
        },
        subtype="html",
    )

    fm = FastMail(conf)

    await fm.send_message(
        message,
        template_name="order_confirmation.html",
    )


async def send_order_status_email(
    email: str,
    name: str,
    order_id: int,
    old_status: str,
    new_status: str,
    updated_at: str,
    tracking_number: str | None = None,
):
    message = MessageSchema(
        subject=f"Order #{order_id} Status Updated",
        recipients=[email],
        template_body={
            "name": name,
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status,
            "updated_at": updated_at,
            "tracking_number": tracking_number,
        },
        subtype="html",
    )

    fm = FastMail(conf)

    await fm.send_message(
        message,
        template_name="order_status_update.html",
    )


async def send_low_stock_email(
    email: str,
    name: str,
    product_name: str,
    product_id: int,
    current_stock: int,
    minimum_stock_level: int,
):
    message = MessageSchema(
        subject=f"Low Stock Alert - {product_name}",
        recipients=[email],
        template_body={
            "name": name,
            "product_name": product_name,
            "product_id": product_id,
            "current_stock": current_stock,
            "minimum_stock_level": minimum_stock_level,
        },
        subtype="html",
    )

    fm = FastMail(conf)

    await fm.send_message(
        message,
        template_name="low_stock.html",
    )

async def send_password_reset_email(
    email: str,
    name: str,
    reset_link: str,
):
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        template_body={
            "name": name,
            "reset_link": reset_link,
        },
        subtype="html",
    )

    fm = FastMail(conf)

    await fm.send_message(
        message,
        template_name="password_reset.html",
    )

