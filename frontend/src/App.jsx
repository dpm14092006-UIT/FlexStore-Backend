import { useState, useCallback } from "react"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { StatsBar } from "@/components/stats-bar"
import { ThemeToggle } from "@/components/theme-toggle"
import { ThemeProvider } from "@/components/theme-provider"
import Visualizer3D from "@/components/Visualizer3D"
import { Expand, Eye, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { packingService } from "@/services/PackingService"

const DEMO_ITEMS = [
    { id: "1", name: "Server Rack", width: 60, height: 180, depth: 100, color: "#3b82f6" },
    { id: "2", name: "Storage Unit", width: 80, height: 80, depth: 80, color: "#06b6d4" },
    { id: "3", name: "Crate A", width: 50, height: 50, depth: 50, color: "#10b981" },
    { id: "4", name: "Crate B", width: 50, height: 50, depth: 50, color: "#f59e0b" },
    { id: "5", name: "Flat Panel", width: 120, height: 15, depth: 100, color: "#8b5cf6" },
    { id: "6", name: "Small Box", width: 30, height: 30, depth: 30, color: "#ec4899" },
]

const DEFAULT_WAREHOUSE = {
    id: "wh-1",
    name: "Main Warehouse",
    bins: [{ id: "bin-1", width: 500, height: 200, depth: 500 }],
    items: DEMO_ITEMS,
    packedData: null
}

function FlexStoreApp() {
    // Multi-Warehouse State
    const [warehouses, setWarehouses] = useState([DEFAULT_WAREHOUSE])
    const [currentWarehouseId, setCurrentWarehouseId] = useState("wh-1")
    const [sidebarOpen, setSidebarOpen] = useState(true)

    const currentWarehouse = warehouses.find(w => w.id === currentWarehouseId) || warehouses[0]

    // Update current warehouse data
    const updateCurrentWarehouse = (updates) => {
        setWarehouses(prev => prev.map(w =>
            w.id === currentWarehouseId ? { ...w, ...updates } : w
        ))
    }

    const setBins = (newBins) => updateCurrentWarehouse({ bins: newBins })
    const setItems = (newItems) => updateCurrentWarehouse({ items: newItems })

    // Helper for safe ID generation
    const generateId = () => Date.now().toString() + Math.random().toString(36).substr(2, 9)

    const addWarehouse = () => {
        const newId = generateId()
        setWarehouses([...warehouses, {
            id: newId,
            name: `Warehouse ${warehouses.length + 1}`,
            bins: [{ id: generateId(), width: 500, height: 200, depth: 500 }],
            items: [],
            packedData: null
        }])
        setCurrentWarehouseId(newId)
    }

    const updateWarehouseName = (id, newName) => {
        setWarehouses(prev => prev.map(w =>
            w.id === id ? { ...w, name: newName } : w
        ))
    }

    const deleteWarehouse = (id) => {
        if (warehouses.length <= 1) {
            alert("Cannot delete the last warehouse.")
            return
        }

        const newWarehouses = warehouses.filter(w => w.id !== id)
        setWarehouses(newWarehouses)

        if (currentWarehouseId === id) {
            setCurrentWarehouseId(newWarehouses[0].id)
        }
    }

    const handleOptimize = async () => {
        try {
            // console.log("Optimizing...", currentWarehouse.bins, currentWarehouse.items)
            // Backend now expects { bins: [], items: [] }
            const result = await packingService.optimize(currentWarehouse.bins, currentWarehouse.items)

            // Result structure: { packed_bins: [], unpacked_items: [], ... }
            updateCurrentWarehouse({ packedData: result })
        } catch (error) {
            alert("Optimization failed. Backend running?")
            console.error(error)
        }
    }

    const handleReset = useCallback(() => {
        updateCurrentWarehouse({ items: [], packedData: null })
    }, [currentWarehouseId])

    // Get current packed items for visualization (flattened from bins if needed, or just first bin for now)
    // For Multi-Bin Generic Visualization, we might need to iterate
    // For now, let's visualize the FIRST bin's packed items or ALL?
    // Let's visualize ALL packed items in 3D space? 
    // Or maybe just the first bin for MVP if Visualizer only supports one?
    // The user wants "Multi-Bin", so Visualizer needs update too.
    // For this step, let's flatten packed items from all bins to show them?
    // But they need 'bin' context. 
    // Let's pass the whole packedData to Visualizer and let it handle or just show first bin.
    const displayPackedItems = currentWarehouse.packedData?.packed_bins?.[0]?.packed_items || []
    const displayBin = currentWarehouse.bins[0] // Simple MVP: Show 1st bin

    return (
        <div className="flex h-screen overflow-hidden bg-background font-sans text-foreground">
            <div className={`shrink-0 transition-all duration-300 ease-in-out overflow-hidden ${sidebarOpen ? "w-80" : "w-0"}`}>
                <div className="w-80 h-full border-r border-border bg-card">
                    <DashboardSidebar
                        warehouses={warehouses}
                        currentId={currentWarehouseId}
                        onSwitch={setCurrentWarehouseId}
                        onAddWarehouse={addWarehouse}
                        onRenameWarehouse={updateWarehouseName}
                        onDeleteWarehouse={deleteWarehouse}
                        warehouse={currentWarehouse}
                        setBins={setBins}
                        setItems={setItems}
                        onOptimize={handleOptimize}
                        onReset={handleReset}
                    />
                </div>
            </div>

            <div className="flex flex-1 flex-col min-w-0">
                <header className="flex items-center justify-between px-5 py-3 bg-card border-b border-border">
                    <div className="flex items-center gap-3">
                        <Button variant="outline" size="icon" className="h-9 w-9 bg-transparent"
                            onClick={() => setSidebarOpen(!sidebarOpen)}>
                            <Expand className="h-4 w-4" />
                        </Button>
                        <div>
                            <h2 className="text-sm font-semibold text-foreground">
                                {currentWarehouse.name} <span className="text-muted-foreground font-normal">({currentWarehouse.bins.length} Zones)</span>
                            </h2>
                            <p className="text-xs text-muted-foreground">Manage storage capacity across locations</p>
                        </div>
                    </div>
                    <ThemeToggle />
                </header>

                <StatsBar
                    bin={displayBin}
                    packedItems={displayPackedItems}
                    totalItems={currentWarehouse.items.length}
                />

                <div className="flex-1 relative">
                    <Visualizer3D bin={displayBin} packedItems={displayPackedItems} />
                    {/* Legend / Stats Overlay */}
                    {currentWarehouse.packedData && currentWarehouse.packedData.packed_bins?.length > 0 && (
                        <div className="absolute top-4 right-4 w-64 p-4 rounded-lg bg-card/90 backdrop-blur border border-border shadow-xl">
                            <h3 className="font-semibold text-sm mb-2">Packing Results</h3>
                            <div className="space-y-2 text-xs">
                                <div className="flex justify-between">
                                    <span>Packed Items:</span>
                                    <span>{currentWarehouse.packedData.packed_count}/{currentWarehouse.packedData.total_items}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Efficiency (Bin 1):</span>
                                    <span>{currentWarehouse.packedData.packed_bins[0]?.efficiency || 0}%</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default function App() {
    return (
        <ThemeProvider attribute="class" defaultTheme="dark">
            <FlexStoreApp />
        </ThemeProvider>
    )
}