from fastapi import APIRouter
from app.api.v1 import auth, categories, products, inventory, orders, payments, reviews, notifications, dashboard, files

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(inventory.router)
api_router.include_router(orders.router)
api_router.include_router(payments.router)
api_router.include_router(reviews.router)
api_router.include_router(notifications.router)
api_router.include_router(dashboard.router)
api_router.include_router(files.router)
