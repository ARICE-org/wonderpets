from fastapi import APIRouter

router = APIRouter(prefix="", tags=["health"])

@router.get("/ping")
def ping():
    return {"message": "pong"}
