from fastapi import APIRouter
router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/agents")
def get_agents():
    return {"success": True}