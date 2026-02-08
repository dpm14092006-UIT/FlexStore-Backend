from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    id: str
    name: str
    width: float
    height: float
    depth: float
    color: str
    # Coordinates (Output)
    x: Optional[float] = 0
    y: Optional[float] = 0
    z: Optional[float] = 0

class Bin(BaseModel):
    width: float
    height: float
    depth: float

class PackingRequest(BaseModel):
    bins: List[Bin]
    items: List[Item]

class PackedBin(BaseModel):
    bin_id: str
    packed_items: List[Item]
    efficiency: float

class PackingResponse(BaseModel):
    packed_bins: List[PackedBin]
    unpacked_items: List[Item]
    total_items: int
    packed_count: int

class HealthCheck(BaseModel):
    status: str
    message: str