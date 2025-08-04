import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import SimulationCreate from './pages/SimulationCreate';
import SimulationDetail from './pages/SimulationDetail';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="simulations/new" element={<SimulationCreate />} />
          <Route path="simulations/:id" element={<SimulationDetail />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;