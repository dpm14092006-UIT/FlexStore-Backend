import os
import shutil

# ==========================================
# FILE CONTENT DEFINITIONS
# ==========================================

# ------------------------------------------
# BACKEND
# ------------------------------------------

BACKEND_REQUIREMENTS = """fastapi
uvicorn
pydantic
"""

BACKEND_MAIN = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.endpoints import router
from app.models.schemas import HealthCheck

app = FastAPI(title="FlexStore 3D API", version="2.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router
app.include_router(router)

@app.get("/", response_model=HealthCheck)
def health_check():
    return {"status": "ok", "message": "FlexStore 3D System Ready"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
"""

BACKEND_INIT = ""

BACKEND_MODELS = """from pydantic import BaseModel
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
    bin: Bin
    items: List[Item]

class PackingResponse(BaseModel):
    packed_items: List[Item]
    unpacked_items: List[Item]
    efficiency: float

class HealthCheck(BaseModel):
    status: str
    message: str
"""

BACKEND_SERVICE_PACKER = """from ..models.schemas import Item, Bin
from typing import List, Tuple

class PackingEngine:
    \"\"\"
    Object-Oriented 3D Bin Packing Engine.
    Uses a Greedy heuristic with space management.
    \"\"\"
    def __init__(self, bin_dims: Bin):
        self.bin_width = bin_dims.width
        self.bin_height = bin_dims.height
        self.bin_depth = bin_dims.depth
        self.packed_items: List[Item] = []
        
    def pack(self, items: List[Item]) -> Tuple[List[Item], List[Item]]:
        \"\"\"
        Main packing method.
        Returns (packed_items, unpacked_items)
        \"\"\"
        # Sort items by volume (Descending) for better efficiency
        sorted_items = sorted(
            items, 
            key=lambda i: i.width * i.height * i.depth, 
            reverse=True
        )
        
        unpacked = []
        
        for item in sorted_items:
            position = self._find_best_position(item)
            if position:
                item.x, item.y, item.z = position
                self.packed_items.append(item)
            else:
                unpacked.append(item)
                
        return self.packed_items, unpacked

    def _find_best_position(self, item: Item):
        \"\"\"
        Finds the first valid position (Greedy) for the item.
        Strategically checks (0,0,0) and corners of existing items.
        \"\"\"
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
"""

BACKEND_API_ENDPOINTS = """from fastapi import APIRouter, HTTPException
from ..models.schemas import PackingRequest, PackingResponse
from ..services.packer import PackingEngine

router = APIRouter()

@router.post("/optimize", response_model=PackingResponse)
def optimize_loading(request: PackingRequest):
    try:
        # Initialize Engine with Bin
        engine = PackingEngine(request.bin)
        
        # Execute Packing
        packed, unpacked = engine.pack(request.items)
        
        # Calculate Stats (Efficiency)
        total_bin_vol = request.bin.width * request.bin.height * request.bin.depth
        used_vol = sum(i.width * i.height * i.depth for i in packed)
        efficiency = (used_vol / total_bin_vol) * 100 if total_bin_vol > 0 else 0
        
        return PackingResponse(
            packed_items=packed,
            unpacked_items=unpacked,
            efficiency=round(efficiency, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

# ------------------------------------------
# FRONTEND
# ------------------------------------------

FRONTEND_PACKAGE = """{
  "name": "flexstore-3d",
  "private": true,
  "version": "2.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.7",
    "clsx": "^2.1.0",
    "lucide-react": "^0.344.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwind-merge": "^2.2.1",
    "three": "^0.161.0",
    "@react-three/fiber": "^8.15.16",
    "@react-three/drei": "^9.99.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.56",
    "@types/react-dom": "^18.2.19",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "vite": "^5.1.4"
  }
}
"""

FRONTEND_VITE_CONFIG = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
"""

FRONTEND_INDEX_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>FlexStore 3D - Intelligent Logistics</title>
    <style>
      body { margin: 0; background: #0f172a; overflow: hidden; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

FRONTEND_TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0f172a',
          surface: '#1e293b',
          border: '#334155'
        },
        primary: {
          DEFAULT: '#8b5cf6', // Violet
          hover: '#7c3aed'
        },
        accent: {
          DEFAULT: '#06b6d4', // Cyan
        }
      }
    },
  },
  plugins: [],
}
"""

FRONTEND_POSTCSS = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

FRONTEND_MAIN_JSX = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

FRONTEND_INDEX_CSS = """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer utilities {
  .glass-panel {
    @apply bg-dark-surface/80 backdrop-blur-md border border-dark-border text-white;
  }
  .input-field {
    @apply bg-dark-bg/50 border border-dark-border rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary;
  }
  .btn-primary {
    @apply bg-gradient-to-r from-primary to-violet-600 hover:from-primary-hover hover:to-violet-700 text-white font-medium py-2 px-4 rounded transition-all shadow-lg hover:shadow-primary/20;
  }
}
"""

FRONTEND_SERVICE_API = """import axios from 'axios';

class FlexStoreClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Send optimization request
   * @param {Object} bin - { width, height, depth }
   * @param {Array} items - List of items
   * @returns {Promise<Object>} - Response data
   */
  async optimize(bin, items) {
    try {
      const response = await this.client.post('/optimize', {
        bin,
        items
      });
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
}

export const apiClient = new FlexStoreClient();
"""

FRONTEND_COMP_UI_CARD = """import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Card = ({ children, className, title }) => {
  return (
    <div className={twMerge("glass-panel rounded-xl p-5 shadow-xl", className)}>
      {title && <h3 className="text-lg font-semibold mb-4 text-accent">{title}</h3>}
      {children}
    </div>
  );
};
"""

FRONTEND_COMP_VISUALIZER = """import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

const ItemMesh = ({ item, binWidth, binHeight, binDepth }) => {
  // Center Calculation
  const width = item.width;
  const height = item.height;
  const depth = item.depth;
  
  // Convert Backend Coords (Corner based) to ThreeJS Coords (Center based)
  // And adjust to center the Bin in the world
  const x = item.x + width / 2 - binWidth / 2;
  const y = item.y + height / 2; // Sit on floor
  const z = item.z + depth / 2 - binDepth / 2;

  return (
    <group position={[x, y, z]}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[width, height, depth]} />
        <meshStandardMaterial 
            color={item.color} 
            roughness={0.2} 
            metalness={0.1}
            transparent={true}
            opacity={0.9}
        />
        <lineSegments>
            <edgesGeometry args={[new THREE.BoxGeometry(width, height, depth)]} />
            <lineBasicMaterial color="black" transparent opacity={0.3} />
        </lineSegments>
      </mesh>
    </group>
  );
};

const BinWireframe = ({ width, height, depth }) => {
  return (
    <group position={[0, height / 2, 0]}>
      {/* Wireframe Outline */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(width, height, depth)]} />
        <lineBasicMaterial color="#38bdf8" linewidth={1} />
      </lineSegments>
      {/* Floor */}
      <mesh position={[0, -height/2 + 0.05, 0]} rotation={[-Math.PI/2, 0, 0]}>
        <planeGeometry args={[width, depth]} />
        <meshBasicMaterial color="#38bdf8" transparent opacity={0.1} />
      </mesh>
    </group>
  );
};

export default function Visualizer3D({ bin, items }) {
  // Camera definition based on bin size
  const camPos = useMemo(() => {
     const maxDim = Math.max(bin.width, bin.height, bin.depth);
     return [maxDim * 1.5, maxDim * 1.2, maxDim * 1.5];
  }, [bin]);

  return (
    <div className="w-full h-full rounded-2xl overflow-hidden shadow-2xl border border-dark-border bg-black/40">
      <Canvas shadows camera={{ position: camPos, fov: 45 }}>
        <fog attach="fog" args={['#0f172a', 10, 100]} />
        <ambientLight intensity={0.6} />
        <spotLight 
            position={[20, 30, 10]} 
            angle={0.3} 
            penumbra={1} 
            intensity={1.5} 
            castShadow 
        />
        <Environment preset="city" />

        <group>
            <BinWireframe width={bin.width} height={bin.height} depth={bin.depth} />
            {items.map((item, idx) => (
                <ItemMesh 
                    key={item.id || idx} 
                    item={item} 
                    binWidth={bin.width} 
                    binHeight={bin.height} 
                    binDepth={bin.depth} 
                />
            ))}
        </group>

        <ContactShadows position={[0, 0, 0]} opacity={0.4} scale={50} blur={2} far={4} color="#000000" />
        <Grid 
            infiniteGrid 
            fadeDistance={50} 
            sectionColor="#475569" 
            cellColor="#1e293b" 
            position={[0, -0.1, 0]}
        />
        <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 2.1} />
      </Canvas>
    </div>
  );
}
"""

FRONTEND_APP_JSX = """import React, { useState } from 'react';
import { Card } from './components/ui/Card';
import Visualizer3D from './components/features/Visualizer3D';
import { apiClient } from './services/api';
import { Package, Box, Layers, Play } from 'lucide-react';

function App() {
  // State
  const [bin, setBin] = useState({ width: 20, height: 15, depth: 20 });
  const [items, setItems] = useState([]);
  const [packedItems, setPackedItems] = useState([]);
  const [efficiency, setEfficiency] = useState(0);
  
  // New Item Input State
  const [newItem, setNewItem] = useState({
    name: '', width: 4, height: 4, depth: 4, color: '#ec4899'
  });

  // Handlers
  const handleAddItem = () => {
    const item = {
      ...newItem,
      id: Math.random().toString(36).substr(2, 9),
      name: newItem.name || `Box ${items.length + 1}`
    };
    setItems([...items, item]);
  };

  const handleValuesChange = (type, field, value) => {
    if (type === 'bin') setBin({ ...bin, [field]: parseFloat(value) || 0 });
    if (type === 'item') setNewItem({ ...newItem, [field]: parseFloat(value) || 0 });
  };

  const handleOptimize = async () => {
    try {
      const result = await apiClient.optimize(bin, items);
      setPackedItems(result.packed_items);
      setEfficiency(result.efficiency);
    } catch (err) {
      alert("Optimization failed. Backend might be offline.");
    }
  };

  return (
    <div className="flex h-screen w-full text-gray-100 font-sans selection:bg-primary selection:text-white">
      
      {/* LEFT SIDEBAR: CONTROLS */}
      <div className="w-[400px] h-full flex flex-col p-6 overflow-y-auto border-r border-dark-border bg-dark-surface/50 backdrop-blur-lg z-10 scrollbar-hide">
        
        {/* Header */}
        <div className="mb-8 flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-primary to-blue-600 rounded-lg shadow-lg">
                <Package size={28} className="text-white" />
            </div>
            <div>
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">FlexStore 3D</h1>
                <p className="text-xs text-gray-500 font-mono tracking-wider">LOGISTICS ENGINE v2.0</p>
            </div>
        </div>

        <div className="space-y-6">
            
            {/* 1. BIN CONFIGURATION */}
            <Card title="Warehouse Dimensions">
                <div className="grid grid-cols-3 gap-3">
                    {['width','height','depth'].map(dim => (
                        <div key={dim}>
                            <label className="text-xs text-gray-400 uppercase font-bold mb-1 block">{dim[0].toUpperCase()}</label>
                            <input 
                                type="number" 
                                className="input-field w-full"
                                value={bin[dim]}
                                onChange={(e) => handleValuesChange('bin', dim, e.target.value)}
                            />
                        </div>
                    ))}
                </div>
            </Card>

            {/* 2. ITEM INPUT */}
            <Card title="New Item">
                 <div className="space-y-3">
                    <input 
                        type="text" 
                        placeholder="Item Name (e.g. TV Box)" 
                        className="input-field w-full"
                        value={newItem.name}
                        onChange={(e) => setNewItem({...newItem, name: e.target.value})}
                    />
                    <div className="grid grid-cols-3 gap-3">
                        {['width','height','depth'].map(dim => (
                            <div key={dim}>
                                <label className="text-xs text-gray-400 uppercase font-bold mb-1 block">{dim[0].toUpperCase()}</label>
                                <input 
                                    type="number" 
                                    className="input-field w-full"
                                    value={newItem[dim]}
                                    onChange={(e) => handleValuesChange('item', dim, e.target.value)}
                                />
                            </div>
                        ))}
                    </div>
                    <div className="flex items-center space-x-3">
                        <input 
                            type="color" 
                            value={newItem.color}
                            onChange={(e) => setNewItem({...newItem, color: e.target.value})}
                            className="h-10 w-12 rounded cursor-pointer bg-transparent border-none"
                        />
                        <button 
                            onClick={handleAddItem}
                            className="flex-1 bg-dark-bg border border-dark-border hover:border-primary/50 text-white py-2 rounded transition-colors flex justify-center items-center space-x-2"
                        >
                            <Layers size={16} /> <span>Add to Queue</span>
                        </button>
                    </div>
                 </div>
            </Card>

            {/* 3. ITEM LIST & ACTION */}
            <div className="flex-1 min-h-[150px]">
                <div className="flex justify-between items-center mb-2">
                    <h3 className="text-sm font-semibold text-gray-400">Queue ({items.length})</h3>
                    {items.length > 0 && 
                        <span className="text-xs text-primary cursor-pointer hover:underline" onClick={() => setItems([])}>Clear All</span>
                    }
                </div>
                <div className="space-y-2 mb-4">
                    {items.slice().reverse().slice(0, 5).map((item, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded bg-dark-bg/40 border border-dark-border/50">
                            <div className="flex items-center space-x-3">
                                <span className="w-3 h-3 rounded-full shadow-lg shadow-white/10" style={{background: item.color}}></span>
                                <span className="text-sm font-medium">{item.name}</span>
                            </div>
                            <span className="text-xs font-mono text-gray-500">{item.width}x{item.height}x{item.depth}</span>
                        </div>
                    ))}
                    {items.length === 0 && <p className="text-center text-gray-600 text-sm py-4 italic">No items in queue...</p>}
                </div>
            
                <button 
                    onClick={handleOptimize}
                    disabled={items.length === 0}
                    className="w-full btn-primary py-4 rounded-xl flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Play size={20} fill="currentColor" />
                    <span className="text-lg tracking-wide">OPTIMIZE LOADING</span>
                </button>
            </div>
            
             {/* STATS */}
             {efficiency > 0 && (
                <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg text-center">
                    <p className="text-xs text-green-400 uppercase tracking-widest font-bold">Efficiency Score</p>
                    <p className="text-3xl font-bold text-white mt-1">{efficiency}%</p>
                </div>
             )}

        </div>
      </div>

      {/* RIGHT: 3D VISUALIZER */}
      <div className="flex-1 h-full relative p-6">
         <Visualizer3D bin={bin} items={packedItems} />
         
         <div className="absolute bottom-10 right-10 text-right opacity-50 pointer-events-none">
            <p className="text-xs font-mono">LEFT CLICK: ROTATE | RIGHT CLICK: PAN | SCROLL: ZOOM</p>
         </div>
      </div>

    </div>
  )
}

export default App
"""


# ==========================================
# FILE WRITING LOGIC
# ==========================================

MAPPINGS = {
    # Backend
    "backend/requirements.txt": BACKEND_REQUIREMENTS,
    "backend/app/__init__.py": BACKEND_INIT,
    "backend/app/main.py": BACKEND_MAIN,
    "backend/app/api/__init__.py": BACKEND_INIT,
    "backend/app/api/endpoints.py": BACKEND_API_ENDPOINTS,
    "backend/app/models/__init__.py": BACKEND_INIT,
    "backend/app/models/schemas.py": BACKEND_MODELS,
    "backend/app/services/__init__.py": BACKEND_INIT,
    "backend/app/services/packer.py": BACKEND_SERVICE_PACKER,

    # Frontend Configuration
    "frontend/package.json": FRONTEND_PACKAGE,
    "frontend/vite.config.js": FRONTEND_VITE_CONFIG,
    "frontend/index.html": FRONTEND_INDEX_HTML,
    "frontend/postcss.config.js": FRONTEND_POSTCSS,
    "frontend/tailwind.config.js": FRONTEND_TAILWIND_CONFIG,
    
    # Frontend Source
    "frontend/src/main.jsx": FRONTEND_MAIN_JSX,
    "frontend/src/index.css": FRONTEND_INDEX_CSS,
    "frontend/src/App.jsx": FRONTEND_APP_JSX,
    "frontend/src/services/api.js": FRONTEND_SERVICE_API,
    "frontend/src/components/ui/Card.jsx": FRONTEND_COMP_UI_CARD,
    "frontend/src/components/features/Visualizer3D.jsx": FRONTEND_COMP_VISUALIZER,
}

def create_project():
    print("🚀 Initializing FlexStore 3D (Enhanced Edition)...")

    # 1. Create Directories
    dirs = [
        "backend/app",
        "backend/app/api",
        "backend/app/models",
        "backend/app/services",
        "frontend/src",
        "frontend/src/services",
        "frontend/src/components/ui",
        "frontend/src/components/features"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"📁 Created: {d}")

    # 2. Write Files
    for filepath, content in MAPPINGS.items():
        filepath = os.path.normpath(filepath)
        # Ensure dir exists for safety
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"📝 Generated: {filepath}")

    print("\\n✨ Project Setup Complete!")
    print("👉 Backend: cd backend && pip install -r requirements.txt && python -m app.main")
    print("👉 Frontend: cd frontend && npm install && npm run dev")

if __name__ == "__main__":
    create_project()
