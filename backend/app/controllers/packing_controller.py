from fastapi import HTTPException
from ..models.schemas import PackingRequest, PackingResponse
from ..services.packer import PackingEngine

class PackingController:
    """
    Controller for handling packing requests.
    Follows OOP principles to separate request handling from business logic.
    """
    def __init__(self):
        self.engine = PackingEngine()

    def optimize(self, request: PackingRequest) -> PackingResponse:
        try:
            # Execute Packing using the engine
            packed_bins, unpacked_items = self.engine.pack(request.bins, request.items)
            
            # Calculate Statistics
            total_items_count = len(request.items)
            packed_items_count = sum(len(b["packed_items"]) for b in packed_bins)
            
            # Construct Response
            return PackingResponse(
                packed_bins=packed_bins,
                unpacked_items=unpacked_items,
                total_items=total_items_count,
                packed_count=packed_items_count
            )
        except Exception as e:
            # Log error here if logging was configured
            raise HTTPException(status_code=500, detail=str(e))
