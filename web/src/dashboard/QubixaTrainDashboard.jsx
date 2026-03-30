import React, { useState, useEffect } from 'react'
import AgentChat from './AgentChat'
import AgentLogs from './AgentLogs'
import AgentControls from './AgentControls'
import PredictionGraph from './PredictionGraph'
import './QubixaTrainDashboard.css'

function QubixaTrainDashboard() {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState('Analyzer Agent')
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [predictions, setPredictions] = useState(null)
  const [uploadedFile, setUploadedFile] = useState(null)

  useEffect(() => {
    // Fetch available agents
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/agents')
      const data = await response.json()
      setAgents(data.agents || [])
    } catch (error) {
      console.error('Error fetching agents:', error)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/analyze/excel', {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      if (data.success) {
        setPredictions(data.predictions)
        setUploadedFile(data.filename)
        alert('Excel file analyzed successfully!')
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Error analyzing Excel file')
    }
  }

  return (
    <div className="dashboard-container fade-in">
      <header className="dashboard-header glass">
        <div className="header-content">
          <h1 className="dashboard-title">
            <span className="gradient-text">Qubixa AI</span>
            <span className="subtitle">Agentic Ad Optimization Platform</span>
          </h1>
          <div className="header-status">
            <label className="upload-button">
              📊 Upload Excel
              <input 
                type="file" 
                accept=".xlsx,.xls,.csv" 
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </label>
            {uploadedFile && <span className="uploaded-file">✓ {uploadedFile}</span>}
            <div className={`status-indicator ${connectionStatus}`}>
              <span className="status-dot"></span>
              <span>{connectionStatus}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <aside className="sidebar glass">
          <h3 className="sidebar-title">Agents</h3>
          <div className="agent-list">
            {agents.map((agent) => (
              <button
                key={agent.name}
                className={`agent-item ${selectedAgent === agent.name ? 'active' : ''}`}
                onClick={() => setSelectedAgent(agent.name)}
              >
                <div className="agent-icon">🤖</div>
                <div className="agent-info">
                  <div className="agent-name">{agent.name}</div>
                  <div className="agent-role">{agent.role}</div>
                </div>
              </button>
            ))}
          </div>
        </aside>

        <main className="main-content">
          <AgentChat 
            agentName={selectedAgent}
            onConnectionChange={setConnectionStatus}
            uploadedFile={uploadedFile}
          />
          {predictions && <PredictionGraph predictions={predictions} />}
        </main>

        <aside className="right-panel">
          <AgentLogs />
          <AgentControls agentName={selectedAgent} />
        </aside>
      </div>
    </div>
  )
}

export default QubixaTrainDashboard
