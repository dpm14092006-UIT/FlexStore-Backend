import React, { useMemo } from 'react';
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