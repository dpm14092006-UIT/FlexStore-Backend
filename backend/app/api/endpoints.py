from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..models.schemas import PackingRequest, PackingResponse
from ..models.sql_models import OptimizationRecord
from ..services.packer import PackingEngine
from ..database import get_db
import json

router = APIRouter()

@router.post("/optimize", response_model=PackingResponse)
def optimize_loading(request: PackingRequest, db: Session = Depends(get_db)):
    try:
        # Initialize Engine with Bin
        engine = PackingEngine(request.bin)
        
        # Execute Packing
        packed, unpacked = engine.pack(request.items)
        
        # Calculate Stats (Efficiency)
        total_bin_vol = request.bin.width * request.bin.height * request.bin.depth
        used_vol = sum(i.width * i.height * i.depth for i in packed)
        efficiency = (used_vol / total_bin_vol) * 100 if total_bin_vol > 0 else 0
        
        # Save to Database
        db_record = OptimizationRecord(
            bin_width=request.bin.width,
            bin_height=request.bin.height,
            bin_depth=request.bin.depth,
            item_count=len(request.items),
            items_json=json.dumps([item.dict() for item in request.items]), # Store inputs
            efficiency=efficiency,
            packed_items_json=json.dumps([item.dict() for item in packed]), # Store results
            unpacked_items_json=json.dumps([item.dict() for item in unpacked])
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return PackingResponse(
            packed_items=packed,
            unpacked_items=unpacked,
            efficiency=round(efficiency, 2)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))