import React, { useState } from 'react'
import './AgentControls.css'

function AgentControls({ agentName }) {
  const [systemPrompt, setSystemPrompt] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [skills, setSkills] = useState([])

  const handleSavePrompt = async () => {
    setIsSaving(true)
    try {
      // API call to save system prompt
      await new Promise(resolve => setTimeout(resolve, 1000))
      alert('System prompt saved!')
    } catch (error) {
      console.error('Error saving prompt:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleScanSkills = async () => {
    try {
      const response = await fetch('/api/skills/scan', { method: 'POST' })
      const data = await response.json()
      alert(`Scanned ${data.skills_loaded} skills`)
    } catch (error) {
      console.error('Error scanning skills:', error)
    }
  }

  return (
    <div className="agent-controls glass">
      <h3 className="controls-title">Training Controls</h3>
      
      <div className="control-section">
        <label className="control-label">System Prompt</label>
        <textarea
          className="control-textarea"
          value={systemPrompt}
          onChange={(e) => setSystemPrompt(e.target.value)}
          placeholder={`Edit system prompt for ${agentName}...`}
          rows={6}
        />
        <button 
          className="control-button primary"
          onClick={handleSavePrompt}
          disabled={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Prompt'}
        </button>
      </div>

      <div className="control-section">
        <button className="control-button" onClick={handleScanSkills}>
          🔄 Scan Skills
        </button>
      </div>
    </div>
  )
}

export default AgentControls
