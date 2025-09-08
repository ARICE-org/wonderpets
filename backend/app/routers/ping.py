from fastapi import APIRouter

router = APIRouter(prefix="", tags=["Health"])

@router.get("/ping")
def ping():
    return {"message": "pong"}
