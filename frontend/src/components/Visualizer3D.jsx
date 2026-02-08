import { useRef, useState, useMemo } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { OrbitControls, ContactShadows, Environment, Edges, Html, Grid } from "@react-three/drei"
import { useTheme } from "next-themes"
import * as THREE from "three"
import { Move, Rotate3D, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"

function WireframeBox({ width, height, depth, position }) {
    return (
        <mesh position={position}>
            <boxGeometry args={[width, height, depth]} />
            <meshBasicMaterial transparent opacity={0} />
            <Edges linewidth={1} threshold={15} color="hsl(217, 91%, 60%)" />
        </mesh>
    )
}

function PackedBox({ item, scale }) {
    const meshRef = useRef(null)
    const [hovered, setHovered] = useState(false)
    const { resolvedTheme } = useTheme()
    const isDark = resolvedTheme === 'dark'

    const w = item.width * scale
    const h = item.height * scale
    const d = item.depth * scale

    // Backend returns bottom-left corner (x,y,z)
    // Three.js needs center (x + w/2, y + h/2, z + d/2)
    const x = (item.x + item.width / 2) * scale
    const y = (item.y + item.height / 2) * scale
    const z = (item.z + item.depth / 2) * scale

    useFrame((_, delta) => {
        if (meshRef.current) {
            const targetScale = hovered ? 1.02 : 1
            meshRef.current.scale.lerp({ x: targetScale, y: targetScale, z: targetScale }, delta * 8)
        }
    })

    const textColor = isDark ? "#ffffff" : "#0f172a"
    const bgColor = isDark ? "rgba(30, 41, 59, 0.9)" : "rgba(255, 255, 255, 0.9)"

    return (
        <mesh ref={meshRef} position={[x, y, z]}
            onPointerOver={(e) => { e.stopPropagation(); setHovered(true) }}
            onPointerOut={() => setHovered(false)} castShadow receiveShadow>
            <boxGeometry args={[w, h, d]} />
            <meshStandardMaterial color={item.color} metalness={0.1} roughness={0.4} transparent opacity={hovered ? 1 : 0.85} />
            <Edges linewidth={hovered ? 2 : 1} threshold={15} color={hovered ? "#ffffff" : "rgba(0,0,0,0.3)"} />
            {hovered && (
                <Html distanceFactor={10} center style={{ pointerEvents: "none" }}>
                    <div className="rounded-lg px-3 py-2 shadow-xl border border-border whitespace-nowrap"
                        style={{ backgroundColor: bgColor, color: textColor }}>
                        <p className="text-sm font-semibold">{item.name}</p>
                        <p className="text-xs opacity-70 font-mono">{item.width} x {item.height} x {item.depth} cm</p>
                    </div>
                </Html>
            )}
        </mesh>
    )
}

export default function Visualizer3D({ bin, packedItems }) {
    if (!bin) {
        return (
            <div className="flex h-full w-full items-center justify-center bg-muted/20 text-muted-foreground">
                <p>No bin selected</p>
            </div>
        )
    }

    const { resolvedTheme } = useTheme()
    const isDark = resolvedTheme === 'dark'
    const [mode, setMode] = useState("rotate") // "rotate" | "pan"
    const controlsRef = useRef()

    const maxDim = Math.max(bin.width, bin.height, bin.depth, 1)
    const scale = 5 / maxDim
    const binW = bin.width * scale
    const binH = bin.height * scale
    const binD = bin.depth * scale

    // Dynamic Colors
    const bgColor = isDark ? "hsl(222, 47%, 6%)" : "#f0f4f8" // Matches --background logic roughly
    const gridCellColor = isDark ? "#1e3a5f" : "#cbd5e1"
    const gridSectionColor = isDark ? "#2563eb" : "#94a3b8"
    const fogColor = isDark ? "hsl(222, 47%, 6%)" : "#f0f4f8"

    return (
        <div className="relative w-full h-full group">
            <Canvas shadows dpr={[1, 1.5]} camera={{ position: [8, 6, 8], fov: 45 }} gl={{ antialias: true }}>
                <color attach="background" args={[bgColor]} />
                <fog attach="fog" args={[fogColor, 10, 50]} />

                <ambientLight intensity={isDark ? 0.4 : 0.7} />
                <spotLight position={[10, 15, 10]} angle={0.3} penumbra={1} intensity={1.5} castShadow shadow-mapSize={[1024, 1024]} />
                <pointLight position={[-10, 5, -10]} intensity={0.5} color={isDark ? "#06b6d4" : "#3b82f6"} />
                <Environment preset={isDark ? "city" : "apartment"} />

                <group position={[-binW / 2, 0, -binD / 2]}>
                    <WireframeBox width={binW} height={binH} depth={binD} position={[binW / 2, binH / 2, binD / 2]} />

                    {packedItems && packedItems.map((item) => (
                        <PackedBox key={item.id} item={item} scale={scale} />
                    ))}

                    <Grid position={[binW / 2, -0.01, binD / 2]} args={[binW * 2, binD * 2]}
                        cellSize={0.5} cellThickness={0.5} cellColor={gridCellColor}
                        sectionSize={2} sectionThickness={1} sectionColor={gridSectionColor}
                        fadeDistance={25} fadeStrength={1} infiniteGrid />

                    <ContactShadows position={[binW / 2, 0, binD / 2]} opacity={0.4} scale={20} blur={2} far={10} frames={1} />
                </group>

                <OrbitControls
                    ref={controlsRef}
                    makeDefault
                    enablePan={true}
                    enableZoom={true}
                    enableRotate={true}
                    minPolarAngle={0}
                    maxPolarAngle={Math.PI / 2.05}
                    target={[0, binH / 2 * scale, 0]}
                    mouseButtons={{
                        LEFT: mode === "rotate" ? THREE.MOUSE.ROTATE : THREE.MOUSE.PAN,
                        MIDDLE: THREE.MOUSE.DOLLY,
                        RIGHT: mode === "rotate" ? THREE.MOUSE.PAN : THREE.MOUSE.ROTATE,
                    }}
                />
            </Canvas>

            {/* Floating Control Toolbar */}
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2 rounded-full border border-border bg-card/90 p-2 shadow-lg backdrop-blur supports-[backdrop-filter]:bg-card/60 transition-opacity opacity-0 group-hover:opacity-100 duration-300">
                <Button
                    variant={mode === "rotate" ? "default" : "ghost"}
                    size="icon"
                    className="h-9 w-9 rounded-full"
                    onClick={() => setMode("rotate")}
                    title="Rotate Mode (Left Click)"
                >
                    <Rotate3D className="h-4 w-4" />
                </Button>
                <Button
                    variant={mode === "pan" ? "default" : "ghost"}
                    size="icon"
                    className="h-9 w-9 rounded-full"
                    onClick={() => setMode("pan")}
                    title="Pan Mode (Left Click)"
                >
                    <Move className="h-4 w-4" />
                </Button>
                <div className="w-px bg-border my-1" />
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-9 w-9 rounded-full hover:bg-destructive/10 hover:text-destructive"
                    onClick={() => controlsRef.current?.reset()}
                    title="Reset View"
                >
                    <RotateCcw className="h-4 w-4" />
                </Button>
            </div>
        </div>
    )
}
