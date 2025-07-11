import './App.css'
import { ModernDashboard } from './components/dashboard/ModernDashboard'

function App() {
  console.log('App component rendering')
  try {
    return <ModernDashboard />
  } catch (error) {
    console.error('Error rendering dashboard:', error)
    return (
      <div style={{ padding: '20px', background: '#000', color: '#fff', minHeight: '100vh' }}>
        <h1>Error Loading Dashboard</h1>
        <p>{error.toString()}</p>
      </div>
    )
  }
}

export default App