import { cn } from "@/lib/utils"

export function CapacityIndicator({ percentage }) {
    const clamped = Math.min(Math.max(percentage, 0), 100)

    const getStatus = () => {
        if (clamped >= 90) return { label: "Near Full", color: "text-red-500", barColor: "bg-red-500", pulse: true }
        if (clamped >= 70) return { label: "Heavy Load", color: "text-amber-500", barColor: "bg-amber-500", pulse: false }
        return { label: "Optimal", color: "text-emerald-500", barColor: "bg-emerald-500", pulse: false }
    }

    const status = getStatus()

    return (
        <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-muted-foreground">Capacity</span>
                <div className="flex items-center gap-2">
                    <span className={cn("text-xs font-semibold", status.color, status.pulse && "animate-pulse-glow")}>
                        {status.label}
                    </span>
                    <span className="text-sm font-mono font-bold text-foreground">{clamped.toFixed(1)}%</span>
                </div>
            </div>
            <div className="h-2.5 w-full rounded-full bg-secondary overflow-hidden">
                <div
                    className={cn("h-full rounded-full transition-all duration-500 ease-out", status.barColor, status.pulse && "animate-pulse-glow")}
                    style={{ width: `${clamped}%` }}
                />
            </div>
        </div>
    )
}
