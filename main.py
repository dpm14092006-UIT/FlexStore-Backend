from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# --- SỬA LỖI 1: CẬP NHẬT IMPORT MỚI ---
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# (Đã chuyển declarative_base từ ext sang orm)

# --- CẤU HÌNH DATABASE: SUPABASE (CLOUD) ---

# 1. Dán cái link trong ảnh vào đây.
# 2. QUAN TRỌNG:
#    - Thay '[YOUR-PASSWORD]' bằng mật khẩu bạn đã đặt lúc tạo project.
#    - Nhớ xóa cả hai dấu ngoặc vuông [] đi nhé!
#    - Ví dụ mật khẩu là 123456 thì viết là: ...:postgres:123456@db....
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.eywmvcndiwqxsmgubwpd:doanZminh1409@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

# 3. Tạo engine
# Lưu ý: XÓA đoạn connect_args={"check_same_thread": False} cũ đi (Cái đó chỉ dùng cho SQLite)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- ĐỊNH NGHĨA BẢNG DỮ LIỆU ---
class BookingDB(Base):
    __tablename__ = "flex_bookings"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    total_volume_m3 = Column(Float)
    total_price = Column(Float)
    packed_items = Column(JSON)
    status = Column(String, default="PENDING")


Base.metadata.create_all(bind=engine)


# --- INPUT MODEL ---
class ItemInput(BaseModel):
    name: str
    width: int
    height: int
    depth: int


class PackingRequest(BaseModel):
    customer_name: str
    warehouse_w: int = 500
    warehouse_h: int = 300
    warehouse_d: int = 400
    items: List[ItemInput]


# --- LOGIC THUẬT TOÁN ---
class Item:
    def __init__(self, name, w, h, d):
        self.name, self.w, self.h, self.d = name, w, h, d
        self.x, self.y, self.z = 0, 0, 0


class WarehouseAlgo:
    def __init__(self, w, h, d):
        self.w, self.h, self.d = w, h, d
        self.packed_items = []

    def check_collision(self, i1, i2):
        return not (i1.x + i1.w <= i2.x or i2.x + i2.w <= i1.x or
                    i1.y + i1.h <= i2.y or i2.y + i2.h <= i1.y or
                    i1.z + i1.d <= i2.z or i2.z + i2.d <= i1.z)

    def fits(self, item):
        return (item.x + item.w <= self.w) and (item.y + item.h <= self.h) and (item.z + item.d <= self.d)

    def add_item(self, new_item):
        candidates = [(0, 0, 0)]
        for i in self.packed_items:
            candidates.append((i.x + i.w, i.y, i.z))
            candidates.append((i.x, i.y + i.h, i.z))
            candidates.append((i.x, i.y, i.z + i.d))
        candidates.sort(key=lambda p: (p[1], p[2], p[0]))

        for p in candidates:
            new_item.x, new_item.y, new_item.z = p
            if self.fits(new_item):
                if not any(self.check_collision(new_item, i) for i in self.packed_items):
                    self.packed_items.append(new_item)
                    return True
        return False


# --- API ---
app = FastAPI()


@app.post("/create-booking")
def create_booking(req: PackingRequest):
    wh = WarehouseAlgo(req.warehouse_w, req.warehouse_h, req.warehouse_d)
    items_obj = [Item(i.name, i.width, i.height, i.depth) for i in req.items]
    items_obj.sort(key=lambda x: x.w * x.h * x.d, reverse=True)

    success_items = []
    failed_items = []

    for item in items_obj:
        if wh.add_item(item):
            success_items.append({
                "name": item.name,
                "x": item.x, "y": item.y, "z": item.z,
                "w": item.w, "h": item.h, "d": item.d
            })
        else:
            failed_items.append(item.name)

    total_vol_m3 = sum([i['w'] * i['h'] * i['d'] for i in success_items]) / 1000000
    estimated_price = max(total_vol_m3 * 50000, 10000)

    db = SessionLocal()
    new_booking = BookingDB(
        customer_name=req.customer_name,
        total_volume_m3=round(total_vol_m3, 4),
        total_price=round(estimated_price, 0),
        packed_items=success_items,
        status="CONFIRMED" if not failed_items else "PARTIAL"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {"booking_id": new_booking.id, "price": new_booking.total_price, "items": success_items}


@app.get("/history")
def get_history():
    db = SessionLocal()
    bookings = db.query(BookingDB).all()
    db.close()
    return bookings


# --- SỬA LỖI 2: THÊM ĐOẠN CHẠY SERVER ---
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)