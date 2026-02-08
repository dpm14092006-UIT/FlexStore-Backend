from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from ..database import Base

class OptimizationRecord(Base):
    __tablename__ = "optimization_records"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Request Data
    bin_width = Column(Float)
    bin_height = Column(Float)
    bin_depth = Column(Float)
    item_count = Column(Integer)
    items_json = Column(JSON)  # Store full item list as JSON
    
    # Result Data
    efficiency = Column(Float)
    packed_items_json = Column(JSON) # Store result
    unpacked_items_json = Column(JSON)
