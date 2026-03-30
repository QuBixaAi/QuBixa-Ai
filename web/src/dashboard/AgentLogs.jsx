import React, { useState, useEffect, useRef } from 'react'
import './AgentLogs.css'

function AgentLogs() {
  const [logs, setLogs] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const logsEndRef = useRef(null)
  const wsRef = useRef(null)

  useEffect(() => {
    connectLogsWebSocket()
    return () => {
      if (wsRef.current) wsRef.current.close()
    }
  }, [])

  const connectLogsWebSocket = () => {
    const clientId = `logs_${Date.now()}`
    const websocket = new WebSocket(`ws://localhost:8000/api/ws/logs/${clientId}`)
    
    websocket.onopen = () => {
      setIsConnected(true)
      addLog('System', 'Log stream connected', 'success')
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'log') {
        addLog('Agent', data.content, data.level)
      }
    }
    
    websocket.onerror = () => {
      setIsConnected(false)
      addLog('System', 'Connection error', 'error')
    }
    
    websocket.onclose = () => {
      setIsConnected(false)
      addLog('System', 'Disconnected', 'warning')
    }
    
    wsRef.current = websocket
  }

  const addLog = (source, message, level = 'info') => {
    const newLog = {
      id: Date.now(),
      source,
      message,
      level,
      timestamp: new Date().toLocaleTimeString()
    }
    setLogs(prev => [...prev.slice(-50), newLog]) // Keep last 50 logs
  }

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const clearLogs = () => {
    setLogs([])
  }

  return (
    <div className="agent-logs glass">
      <div className="logs-header">
        <h3 className="logs-title">Agent Logs</h3>
        <div className="logs-actions">
          <span className={`connection-dot ${isConnected ? 'connected' : ''}`}></span>
          <button className="clear-button" onClick={clearLogs}>Clear</button>
        </div>
      </div>
      
      <div className="logs-container">
        {logs.length === 0 ? (
          <div className="logs-empty">
            <p>No logs yet...</p>
          </div>
        ) : (
          logs.map(log => (
            <div key={log.id} className={`log-entry ${log.level} slide-in`}>
              <span className="log-time">{log.timestamp}</span>
              <span className="log-source">[{log.source}]</span>
              <span className="log-message">{log.message}</span>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  )
}

export default AgentLogs
