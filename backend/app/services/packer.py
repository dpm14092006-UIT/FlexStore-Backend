from ..models.schemas import Item, Bin
from typing import List, Tuple

class PackingEngine:
    """
    Object-Oriented 3D Bin Packing Engine.
    Uses a Greedy heuristic with space management.
    """
    def __init__(self):
        self.bin_width = 0
        self.bin_height = 0
        self.bin_depth = 0
        self.packed_items: List[Item] = []
        
    def pack(self, bins: List[Bin], items: List[Item]) -> Tuple[List[dict], List[Item]]:
        """
        Main packing method for multiple bins.
        Returns (packed_bins, unpacked_items)
        """
        # Sort items by volume (Descending) for better efficiency
        sorted_items = sorted(
            items, 
            key=lambda i: i.width * i.height * i.depth, 
            reverse=True
        )
        
        packed_bins_result = []
        current_items_to_pack = sorted_items[:]
        
        for idx, bin_dims in enumerate(bins):
            if not current_items_to_pack:
                break
                
            self.bin_width = bin_dims.width
            self.bin_height = bin_dims.height
            self.bin_depth = bin_dims.depth
            self.packed_items = []
            
            # Temporary list for items that didn't fit in THIS bin
            unpacked_in_this_bin = []
            
            for item in current_items_to_pack:
                position = self._find_best_position(item)
                if position:
                    item.x, item.y, item.z = position
                    self.packed_items.append(item)
                else:
                    unpacked_in_this_bin.append(item)
            
            # Calculate efficiency for this bin
            bin_vol = self.bin_width * self.bin_height * self.bin_depth
            used_vol = sum(i.width * i.height * i.depth for i in self.packed_items)
            efficiency = (used_vol / bin_vol) * 100 if bin_vol > 0 else 0
            
            packed_bins_result.append({
                "bin_id": f"Bin {idx + 1}",
                "packed_items": self.packed_items[:], # Copy list
                "efficiency": round(efficiency, 2)
            })
            
            # Update items for next bin
            current_items_to_pack = unpacked_in_this_bin[:]
            
        return packed_bins_result, current_items_to_pack

    def _find_best_position(self, item: Item):
        """
        Finds the first valid position (Greedy) for the item.
        Strategically checks (0,0,0) and corners of existing items.
        """
        # Potential pivot points
        candidates = [(0, 0, 0)]
        for other in self.packed_items:
            # Add points adjacent to existing items
            candidates.append((other.x + other.width, other.y, other.z))
            candidates.append((other.x, other.y + other.height, other.z))
            candidates.append((other.x, other.y, other.z + other.depth))
            
        # Optimize search: Sort candidates by proximity to origin (0,0,0)
        # This keeps the packing dense towards the corner
        candidates.sort(key=lambda p: p[0]**2 + p[1]**2 + p[2]**2)
        
        for x, y, z in candidates:
            if self._can_fit(item, x, y, z):
                return (x, y, z)
        return None

    def _can_fit(self, item: Item, x: float, y: float, z: float) -> bool:
        # Check Bin Boundaries
        if (x + item.width > self.bin_width or 
            y + item.height > self.bin_height or 
            z + item.depth > self.bin_depth):
            return False
            
        # Check Collisions
        for other in self.packed_items:
            if self._intersect(item, x, y, z, other):
                return False
        return True

    def _intersect(self, item: Item, x, y, z, other: Item) -> bool:
        return (
            x < other.x + other.width and x + item.width > other.x and
            y < other.y + other.height and y + item.height > other.y and
            z < other.z + other.depth and z + item.depth > other.z
        )