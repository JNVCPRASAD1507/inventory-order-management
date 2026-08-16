import asyncio

from app.services.email_service import send_otp_email


async def main():
    await send_otp_email(
        email="chandu@gmail.com",
        name="Prasad",
        otp="123456",
    )

    print("Email sent successfully!")


if __name__ == "__main__":
    asyncio.run(main())