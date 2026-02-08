# FlexStore 3D - Setup & Run Guide

The application has been refactored to use **React (Vite)** for the frontend and **Python (FastAPI)** for the backend.

## Prerequisites
- Node.js (v18+)
- Python (v3.8+)

## 1. Start the Backend (Python)
The backend runs the packing algorithm and API.

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```
*Server will start at `http://localhost:8000`*

## 2. Start the Frontend (React)
The frontend provides the 3D visualization and user interface.

```bash
cd frontend
npm install
npm run dev
```
*Open your browser at `http://localhost:5173`*

## Features
- **3D Visualization**: See your items packed in real-time.
- **Drag & Drop**: Rotate and zoom the 3D view.
- **Custom Items**: Add items with specific dimensions and colors.
- **Optimization**: Click "Optimize Packing" to let the Python algorithm calculate the best fit.
