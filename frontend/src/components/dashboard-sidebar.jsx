import { useState } from "react"
import { Box, Plus, Trash2, Package, RotateCcw, Warehouse, ChevronDown, ChevronUp, Palette, Pencil } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { CapacityIndicator } from "@/components/capacity-indicator"
import { HexColorPicker } from "react-colorful"

const PRESETS = [
    { label: "S", name: "Small Box", w: 30, h: 30, d: 30 },
    { label: "M", name: "Medium Box", w: 60, h: 60, d: 60 },
    { label: "L", name: "Large Box", w: 100, h: 100, d: 100 },
    { label: "Pallet", name: "Pallet", w: 120, h: 15, d: 100 },
]

const COLORS = [
    "#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#f97316",
    "#14b8a6", "#84cc16", "#eab308", "#f43f5e", "#a855f7", "#6366f1", "#0ea5e9", "#22c55e",
    "#fb923c", "#fbbf24", "#facc15", "#a3e635", "#4ade80", "#2dd4bf", "#38bdf8", "#818cf8"
]

export function DashboardSidebar({
    warehouses, currentId, onSwitch, onAddWarehouse, onRenameWarehouse, onDeleteWarehouse,
    warehouse, setBins, setItems, onOptimize, onReset,
}) {
    const { bins, items, packedData } = warehouse
    const [editingId, setEditingId] = useState(null)
    const [editName, setEditName] = useState("")

    // Helper for safe ID generation
    const generateId = () => Date.now().toString() + Math.random().toString(36).substr(2, 9)

    // Local state for adding items (kept as is)
    const [newItem, setNewItem] = useState({
        name: "", width: 50, height: 50, depth: 50, color: "#3b82f6",
    })
    const [showItemForm, setShowItemForm] = useState(false)
    const [showColorPicker, setShowColorPicker] = useState(false)

    // Derived state
    const packedCount = packedData?.packed_count || 0
    const totalCount = items.length
    const totalVolume = bins.reduce((acc, b) => acc + (b.width * b.height * b.depth), 0)
    const usedVolume = packedData?.packed_bins?.reduce((acc, b) => acc + b.packed_items.reduce((v, i) => v + (i.width * i.height * i.depth), 0), 0) || 0
    const capacity = totalVolume > 0 ? (usedVolume / totalVolume) * 100 : 0

    const addItem = () => {
        if (!newItem.name.trim()) return
        const item = { ...newItem, id: generateId() }
        setItems([...items, item])
        setNewItem({ name: "", width: 50, height: 50, depth: 50, color: "#3b82f6" })
        setShowItemForm(false)
    }

    const removeItem = (id) => {
        setItems(items.filter((item) => item.id !== id))
    }

    const addPreset = (preset) => {
        const item = {
            id: generateId(), name: preset.name,
            width: preset.w, height: preset.h, depth: preset.d,
            color: COLORS[items.length % COLORS.length],
        }
        setItems([...items, item])
    }

    const updateBin = (binId, key, value) => {
        const newBins = bins.map(b => b.id === binId ? { ...b, [key]: Number(value) || 0 } : b)
        setBins(newBins)
    }

    const addBin = () => {
        setBins([...bins, { id: generateId(), width: 500, height: 200, depth: 500 }])
    }

    const removeBin = (binId) => {
        if (bins.length <= 1) return
        setBins(bins.filter(b => b.id !== binId))
    }

    return (
        <div className="flex h-full flex-col bg-card border-r border-border">
            <div className="flex items-center gap-3 px-5 py-4 border-b border-border">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                    <Package className="h-5 w-5 text-primary-foreground" />
                </div>
                <div>
                    <h1 className="text-base font-bold text-foreground tracking-tight">Manage Warehouse</h1>
                    <p className="text-xs text-muted-foreground">Logistics Optimizer</p>
                </div>
            </div>

            <ScrollArea className="flex-1">
                <div className="flex flex-col gap-5 p-5">
                    {/* Warehouse Switcher */}
                    <section>
                        <div className="flex items-center justify-between mb-3">
                            <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Locations</Label>
                            <Button variant="ghost" size="icon" className="h-5 w-5" onClick={onAddWarehouse} title="Add Warehouse">
                                <Plus className="h-3 w-3" />
                            </Button>
                        </div>
                        {/* ... warehouse list ... */}
                        <div className="flex flex-col gap-2">
                            {warehouses.map(w => (
                                <div key={w.id}
                                    onClick={() => onSwitch(w.id)}
                                    className={`flex items-center justify-between px-2 py-1.5 rounded-md text-sm transition-colors group cursor-pointer ${w.id === currentId ? "bg-accent/50" : "hover:bg-accent/30"}`}>
                                    {/* ... rest of warehouse item ... */}
                                    {editingId === w.id ? (
                                        <div className="flex items-center flex-1 gap-1" onClick={e => e.stopPropagation()}>
                                            <Input
                                                value={editName}
                                                onChange={(e) => setEditName(e.target.value)}
                                                className="h-7 text-xs"
                                                autoFocus
                                                onBlur={() => {
                                                    if (editName.trim()) onRenameWarehouse(w.id, editName)
                                                    setEditingId(null)
                                                }}
                                                onKeyDown={(e) => {
                                                    if (e.key === "Enter") {
                                                        if (editName.trim()) onRenameWarehouse(w.id, editName)
                                                        setEditingId(null)
                                                    }
                                                }}
                                            />
                                        </div>
                                    ) : (
                                        <div className={`flex-1 text-left truncate px-2 py-1 ${w.id === currentId ? "font-medium text-primary" : "text-foreground"}`}>
                                            {w.name}
                                            <Badge variant={w.id === currentId ? "secondary" : "outline"} className="text-[10px] h-4 px-1 ml-2 inline-flex">
                                                {w.bins.length}
                                            </Badge>
                                        </div>
                                    )}

                                    {/* Action Buttons (Visible on Hover or Active) */}
                                    <div className={`flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity ${w.id === currentId || editingId === w.id ? "opacity-100" : ""}`}>
                                        {/* Rename Button */}
                                        <Button
                                            variant="ghost" size="icon" className="h-6 w-6 text-muted-foreground hover:text-foreground"
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                setEditingId(w.id)
                                                setEditName(w.name)
                                            }}
                                        >
                                            <Pencil className="h-3 w-3" />
                                        </Button>

                                        {/* Delete Button */}
                                        <Button
                                            variant="ghost" size="icon" className="h-6 w-6 text-muted-foreground hover:text-destructive"
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                if (window.confirm(`Delete "${w.name}"?`)) onDeleteWarehouse(w.id)
                                            }}
                                            disabled={warehouses.length <= 1}
                                        >
                                            <Trash2 className="h-3 w-3" />
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    <Separator />

                    {/* Storage Options */}
                    <section>
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                                <Warehouse className="h-4 w-4 text-primary" />
                                <h2 className="text-sm font-semibold text-foreground">Storage Zones</h2>
                            </div>
                            {/* Add Zone button removed */}
                        </div>

                        <div className="space-y-4">
                            {bins.map((bin, idx) => (
                                <div key={bin.id} className="relative group">
                                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                                        <span>Zone #{idx + 1}</span>
                                        {bins.length > 1 && (
                                            <button onClick={() => removeBin(bin.id)} className="text-destructive hover:underline">Remove</button>
                                        )}
                                    </div>
                                    <div className="grid grid-cols-3 gap-2">
                                        <div>
                                            <Label className="text-[10px] text-muted-foreground mb-1 block">W</Label>
                                            <Input type="number" value={bin.width}
                                                onChange={(e) => updateBin(bin.id, 'width', e.target.value)}
                                                className="h-8 font-mono text-xs" />
                                        </div>
                                        <div>
                                            <Label className="text-[10px] text-muted-foreground mb-1 block">H</Label>
                                            <Input type="number" value={bin.height}
                                                onChange={(e) => updateBin(bin.id, 'height', e.target.value)}
                                                className="h-8 font-mono text-xs" />
                                        </div>
                                        <div>
                                            <Label className="text-[10px] text-muted-foreground mb-1 block">D</Label>
                                            <Input type="number" value={bin.depth}
                                                onChange={(e) => updateBin(bin.id, 'depth', e.target.value)}
                                                className="h-8 font-mono text-xs" />
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    <Separator />

                    <section>
                        <CapacityIndicator percentage={capacity} />
                        <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                            <span>Packed: {packedCount}/{totalCount} items</span>
                            <span>{totalVolume.toLocaleString()} cm&sup3;</span>
                        </div>
                    </section>

                    <Separator />

                    <section>
                        <div className="flex items-center gap-2 mb-3">
                            <Box className="h-4 w-4 text-primary" />
                            <h2 className="text-sm font-semibold text-foreground">Quick Add Items</h2>
                        </div>
                        <div className="grid grid-cols-4 gap-2">
                            {PRESETS.map((preset) => (
                                <Button key={preset.label} variant="outline" size="sm"
                                    className="h-9 text-xs font-medium bg-transparent"
                                    onClick={() => addPreset(preset)}>
                                    {preset.label}
                                </Button>
                            ))}
                        </div>
                    </section>

                    <Separator />

                    <section>
                        <button type="button" className="flex w-full items-center justify-between mb-3 group"
                            onClick={() => setShowItemForm(!showItemForm)}>
                            <div className="flex items-center gap-2">
                                <Plus className="h-4 w-4 text-primary" />
                                <h2 className="text-sm font-semibold text-foreground">Custom Item</h2>
                            </div>
                            {showItemForm ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                        </button>

                        {showItemForm && (
                            <div className="flex flex-col gap-3 rounded-lg bg-secondary/50 p-3">
                                <div>
                                    <Label className="text-xs text-muted-foreground mb-1 block">Name</Label>
                                    <Input value={newItem.name}
                                        onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                                        placeholder="e.g. Heavy Crate" className="h-9 text-sm" />
                                </div>
                                <div className="grid grid-cols-3 gap-2">
                                    <div>
                                        <Label className="text-xs text-muted-foreground mb-1 block">W</Label>
                                        <Input type="number" value={newItem.width}
                                            onChange={(e) => setNewItem({ ...newItem, width: Number(e.target.value) || 0 })}
                                            className="h-9 font-mono text-sm" />
                                    </div>
                                    <div>
                                        <Label className="text-xs text-muted-foreground mb-1 block">H</Label>
                                        <Input type="number" value={newItem.height}
                                            onChange={(e) => setNewItem({ ...newItem, height: Number(e.target.value) || 0 })}
                                            className="h-9 font-mono text-sm" />
                                    </div>
                                    <div>
                                        <Label className="text-xs text-muted-foreground mb-1 block">D</Label>
                                        <Input type="number" value={newItem.depth}
                                            onChange={(e) => setNewItem({ ...newItem, depth: Number(e.target.value) || 0 })}
                                            className="h-9 font-mono text-sm" />
                                    </div>
                                </div>
                                <div>
                                    <Label className="text-xs text-muted-foreground mb-1.5 flex items-center gap-1">
                                        <Palette className="h-3 w-3" /> Color
                                    </Label>

                                    {/* Quick Preset Colors */}
                                    <div className="flex flex-wrap items-center gap-1.5 mb-2">
                                        {COLORS.slice(0, 12).map((c) => (
                                            <button key={c} type="button"
                                                className="h-6 w-6 rounded-md border-2 transition-transform hover:scale-110"
                                                style={{ backgroundColor: c, borderColor: newItem.color === c ? "hsl(var(--foreground))" : "transparent" }}
                                                onClick={() => setNewItem({ ...newItem, color: c })} />
                                        ))}
                                    </div>

                                    {/* Advanced Color Picker Toggle */}
                                    <Button
                                        type="button"
                                        variant="outline"
                                        size="sm"
                                        className="w-full h-8 text-xs"
                                        onClick={() => setShowColorPicker(!showColorPicker)}
                                    >
                                        <Palette className="h-3 w-3 mr-1.5" />
                                        {showColorPicker ? "Hide" : "Show"} Advanced Picker
                                    </Button>

                                    {/* Advanced Color Picker */}
                                    {showColorPicker && (
                                        <div className="mt-2 p-3 rounded-lg border border-border bg-background/50">
                                            <HexColorPicker color={newItem.color} onChange={(color) => setNewItem({ ...newItem, color })} />
                                            <div className="mt-2 flex items-center gap-2">
                                                <Input
                                                    type="text"
                                                    value={newItem.color}
                                                    onChange={(e) => setNewItem({ ...newItem, color: e.target.value })}
                                                    className="h-8 font-mono text-xs"
                                                    placeholder="#000000"
                                                />
                                                <div className="h-8 w-12 rounded border border-border shrink-0" style={{ backgroundColor: newItem.color }} />
                                            </div>
                                        </div>
                                    )}
                                </div>
                                <Button onClick={addItem} size="sm" className="w-full mt-1">
                                    <Plus className="h-4 w-4 mr-1" /> Add Item
                                </Button>
                            </div>
                        )}
                    </section>

                    <Separator />

                    <section>
                        <div className="flex items-center justify-between mb-3">
                            <h2 className="text-sm font-semibold text-foreground">Items ({items.length})</h2>
                        </div>
                        {items.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-6 text-center">
                                <Box className="h-8 w-8 text-muted-foreground/40 mb-2" />
                                <p className="text-xs text-muted-foreground">No items added yet.</p>
                                <p className="text-xs text-muted-foreground">Use presets or add custom items above.</p>
                            </div>
                        ) : (
                            <div className="flex flex-col gap-1.5">
                                {items.map((item) => (
                                    <div key={item.id} className="flex items-center gap-2.5 rounded-lg bg-secondary/50 px-3 py-2 group">
                                        <div className="h-4 w-4 rounded shrink-0" style={{ backgroundColor: item.color }} />
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-foreground truncate">{item.name}</p>
                                            <p className="text-xs text-muted-foreground font-mono">{item.width} x {item.height} x {item.depth}</p>
                                        </div>
                                        <Badge variant="secondary" className="text-xs font-mono shrink-0">
                                            {(item.width * item.height * item.depth).toLocaleString()}
                                        </Badge>
                                        <Button variant="ghost" size="icon"
                                            className="h-7 w-7 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive"
                                            onClick={() => removeItem(item.id)}>
                                            <Trash2 className="h-3.5 w-3.5" />
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>
                </div>
            </ScrollArea>

            <div className="border-t border-border p-4 flex flex-col gap-2">
                <Button onClick={onOptimize} className="w-full" disabled={items.length === 0}>
                    <Package className="h-4 w-4 mr-2" /> Optimize Packing
                </Button>
                <Button variant="outline" onClick={onReset} className="w-full bg-transparent" size="sm">
                    <RotateCcw className="h-3.5 w-3.5 mr-1.5" /> Reset All
                </Button>
            </div>
        </div >
    )
}
