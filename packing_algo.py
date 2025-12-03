class Item:
    def __init__(self, name, width, height, depth):
        self.name = name
        self.w = width  # Chiều rộng (x)
        self.h = height  # Chiều cao (y)
        self.d = depth  # Chiều sâu (z)
        # Tọa độ của góc dưới-trái-trong cùng của kiện hàng
        self.x = 0
        self.y = 0
        self.z = 0
        self.volume = width * height * depth

    def get_dimension(self):
        return [self.w, self.h, self.d]


class Warehouse:
    def __init__(self, width, height, depth):
        self.w = width
        self.h = height
        self.d = depth
        self.items = []  # Danh sách hàng đã xếp vào kho

    # --- HÀM QUAN TRỌNG NHẤT: KIỂM TRA VA CHẠM ---
    # Kiểm tra xem item mới (new_item) có đè lên item cũ (exist_item) không?
    def check_collision(self, item1, item2):
        # Logic: 2 vật KHÔNG va chạm nếu chúng nằm tách biệt hoàn toàn theo ít nhất 1 trục

        # Kiểm tra trục X (Chiều rộng)
        no_overlap_x = (item1.x + item1.w <= item2.x) or (item2.x + item2.w <= item1.x)
        # Kiểm tra trục Y (Chiều cao)
        no_overlap_y = (item1.y + item1.h <= item2.y) or (item2.y + item2.h <= item1.y)
        # Kiểm tra trục Z (Chiều sâu)
        no_overlap_z = (item1.z + item1.d <= item2.z) or (item2.z + item2.d <= item1.z)

        # Nếu tách biệt ở bất kỳ trục nào -> Không va chạm -> Trả về False
        if no_overlap_x or no_overlap_y or no_overlap_z:
            return False

        return True  # Có va chạm

    # Kiểm tra xem item có nằm gọn trong kho không?
    def fits_in_warehouse(self, item):
        return (item.x + item.w <= self.w) and \
            (item.y + item.h <= self.h) and \
            (item.z + item.d <= self.d)

    # --- THUẬT TOÁN XẾP HÀNG (Phiên bản đơn giản: First Fit) ---
    def add_item(self, new_item):
        # Chiến thuật: Quét các điểm trong không gian kho để tìm chỗ đặt
        # (Để đơn giản cho bản Demo, ta sẽ thử đặt new_item ngay cạnh các item cũ)

        potential_points = [(0, 0, 0)]  # Luôn thử góc (0,0,0) đầu tiên

        for item in self.items:
            # Thêm các điểm "ứng viên" nằm ngay bên cạnh các item đã có
            potential_points.append((item.x + item.w, item.y, item.z))  # Bên phải
            potential_points.append((item.x, item.y + item.h, item.z))  # Bên trên
            potential_points.append((item.x, item.y, item.z + item.d))  # Phía trước

        # Sắp xếp các điểm ứng viên để ưu tiên lấp đầy từ góc (0,0,0) trở đi -> Tối ưu không gian
        potential_points.sort(key=lambda p: (p[2], p[1], p[0]))

        for point in potential_points:
            new_item.x, new_item.y, new_item.z = point

            # 1. Kiểm tra xem có lòi ra khỏi kho không?
            if not self.fits_in_warehouse(new_item):
                continue  # Bỏ qua điểm này, thử điểm tiếp theo

            # 2. Kiểm tra xem có đè lên item nào khác không?
            collision = False
            for exist_item in self.items:
                if self.check_collision(new_item, exist_item):
                    collision = True
                    break

            # Nếu không va chạm gì cả -> Đặt hàng vào đây!
            if not collision:
                self.items.append(new_item)
                print(f"✅ Đã xếp: {new_item.name} tại tọa độ ({new_item.x}, {new_item.y}, {new_item.z})")
                return True

        print(f"❌ Không thể xếp: {new_item.name} (Kho đầy hoặc không vừa kích thước)")
        return False


# --- CHẠY THỬ NGHIỆM (TEST CASE) ---

# 1. Khởi tạo kho (Ví dụ: Rộng 100, Cao 100, Sâu 100)
my_warehouse = Warehouse(100, 100, 100)

# 2. Tạo danh sách hàng cần gửi
# Mẹo: Sắp xếp hàng to xếp trước để tối ưu (Logic FFD)
packages = [
    Item("Tủ lạnh", 50, 80, 50),
    Item("Thùng Mì 1", 30, 20, 40),
    Item("Thùng Mì 2", 30, 20, 40),
    Item("Thùng Mì 3", 30, 20, 40),
    Item("TV 65 inch", 10, 90, 140),  # Cái này dài quá khổ so với kho
]

print("--- BẮT ĐẦU XẾP HÀNG ---")
for pkg in packages:
    my_warehouse.add_item(pkg)

print(f"\nTổng số kiện đã xếp được: {len(my_warehouse.items)}")