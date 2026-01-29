from fastapi import APIRouter


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/")
async def get_all_products():
    """Returns a list of all products"""
    return {"message": "Список всех товаров"}


@router.post("/")
async def create_product():
    """Create a new product"""
    return {"message": "Товар создан"}


@router.get("/category/{category_id}")
async def get_products_by_category(category_id: int):
    """Get all products from category by category_id"""
    return {"message": f"Товары в категории ID={category_id}"}


@router.get("/{product_id}")
async def get_product(product_id: int):
    """Get details of product by id"""
    return {"message": f"Детали товара ID={product_id}"}


@router.put("/{product_id}")
async def update_product(product_id: int):
    """Update product by id"""
    return {"message": f"Товар ID={product_id} обновлён"}


@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """Delete product by id"""
    return {"message": f"Товар ID={product_id} удалён"}