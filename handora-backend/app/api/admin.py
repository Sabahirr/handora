from fastapi import APIRouter

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/ping")
def ping():
    return {"message": "Admin router is working"}
