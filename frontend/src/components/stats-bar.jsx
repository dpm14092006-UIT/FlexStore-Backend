import { Box, Layers, TrendingUp, Maximize } from "lucide-react"

export function StatsBar({ bin, packedItems, totalItems }) {
    const binVolume = bin.width * bin.height * bin.depth
    const usedVolume = packedItems.reduce((acc, item) => acc + item.width * item.height * item.depth, 0)
    const efficiency = binVolume > 0 ? ((usedVolume / binVolume) * 100).toFixed(1) : "0.0"

    const stats = [
        { label: "Bin Volume", value: `${binVolume.toLocaleString()} cm\u00B3`, icon: Maximize },
        { label: "Used Volume", value: `${usedVolume.toLocaleString()} cm\u00B3`, icon: Layers },
        { label: "Items Packed", value: `${packedItems.length} / ${totalItems}`, icon: Box },
        { label: "Efficiency", value: `${efficiency}%`, icon: TrendingUp },
    ]

    return (
        <div className="flex items-center gap-6 px-5 py-3 bg-card border-b border-border overflow-x-auto">
            {stats.map((stat) => (
                <div key={stat.label} className="flex items-center gap-2.5 shrink-0">
                    <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10">
                        <stat.icon className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                        <p className="text-xs text-muted-foreground">{stat.label}</p>
                        <p className="text-sm font-semibold font-mono text-foreground">{stat.value}</p>
                    </div>
                </div>
            ))}
        </div>
    )
}
