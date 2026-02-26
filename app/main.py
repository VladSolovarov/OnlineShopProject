from fastapi import FastAPI
from app.routers import categories, products, users, reviews

app = FastAPI(
    title='Проект: Онлайн-магазин',
    version='0.1.0',
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)

@app.get('/')
async def root():
    """Root path to see API is working"""
    return {'message': "Добро пожаловать в API магазина!"}

