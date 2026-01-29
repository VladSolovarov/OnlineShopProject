from fastapi import APIRouter


router = APIRouter(
    prefix='/categories',
    tags=['categories']
)

@router.get('/')
async def get_all_categories():
    """Returns a list of all categories"""
    return {'message': ''}


@router.post('/')
async def create_category():
    """Create category"""
    return {'message': ''}


@router.put('/')
async def update_category(id: int):
    """Update category by id"""
    return {'message': f'Категория ID={id} обновлена.'}


@router.delete('/')
async def delete_category(id: int):
    """Delete category by id"""
    return {'message': f'Категория ID={id} удалена'}