from fastapi import APIRouter
from ..models.schemas import PackingRequest, PackingResponse
from ..controllers.packing_controller import PackingController

router = APIRouter()
controller = PackingController()

@router.post("/optimize", response_model=PackingResponse)
def optimize_loading(request: PackingRequest):
    return controller.optimize(request)