# AMS Frontend

Article Market Simulator Dashboard - React TypeScript frontend for visualizing multi-agent article evaluations.

## Features

- 📊 Real-time simulation monitoring with WebSocket updates
- 📈 Interactive data visualizations (charts, radar plots)
- 🎨 Modern UI with Tailwind CSS
- 🌓 Dark mode support
- 📱 Responsive design

## Tech Stack

- React 19 with TypeScript
- Vite for fast development
- React Router for navigation
- Recharts for data visualization
- Tailwind CSS for styling
- Axios for API calls
- WebSockets for real-time updates

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure API endpoint (optional):
```bash
# Default is http://localhost:8000
# To change, edit .env file:
VITE_API_URL=http://your-api-url
```

3. Start development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Build

```bash
npm run build
```

Build artifacts will be in the `dist` directory.

## Integration with Backend

Make sure the FastAPI backend is running on port 8000:

```bash
cd ../
poetry run uvicorn src.server.app:app --reload
```

## Pages

- **Dashboard** (`/`) - Overview of all simulations
- **Create Simulation** (`/simulations/new`) - Create new article evaluation
- **Simulation Detail** (`/simulations/:id`) - View results and real-time progress

## Components Structure

```
src/
├── components/
│   └── Layout.tsx          # Main layout with navigation
├── pages/
│   ├── Dashboard.tsx       # Simulations list
│   ├── SimulationCreate.tsx # New simulation form
│   └── SimulationDetail.tsx # Results & real-time updates
├── services/
│   └── api.ts             # API client & WebSocket
└── types/
    └── api.ts             # TypeScript types matching backend
```