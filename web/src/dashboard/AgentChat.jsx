import React, { useState, useEffect, useRef } from 'react'
import './AgentChat.css'

function AgentChat({ agentName, onConnectionChange, uploadedFile }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [ws, setWs] = useState(null)
  const messagesEndRef = useRef(null)
  const clientId = useRef(`client_${Date.now()}`)

  useEffect(() => {
    connectWebSocket()
    return () => {
      if (ws) ws.close()
    }
  }, [])

  const connectWebSocket = () => {
    const websocket = new WebSocket(`ws://localhost:8000/api/ws/${clientId.current}`)
    
    websocket.onopen = () => {
      console.log('WebSocket connected')
      onConnectionChange('connected')
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('Received:', data)
      handleWebSocketMessage(data)
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
      onConnectionChange('disconnected')
    }
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected')
      onConnectionChange('disconnected')
      // Attempt reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000)
    }
    
    setWs(websocket)
  }

  const handleWebSocketMessage = (data) => {
    console.log('Message type:', data.type, 'Content:', data.content)
    
    if (data.type === 'token') {
      // Append streaming token to last message
      setMessages(prev => {
        const newMessages = [...prev]
        const lastMsg = newMessages[newMessages.length - 1]
        if (lastMsg && lastMsg.sender === 'agent' && lastMsg.streaming) {
          lastMsg.content += data.content
        } else {
          newMessages.push({
            sender: 'agent',
            content: data.content,
            streaming: true,
            timestamp: new Date()
          })
        }
        return newMessages
      })
    } else if (data.type === 'complete') {
      // Mark streaming as complete
      setMessages(prev => {
        const newMessages = [...prev]
        const lastMsg = newMessages[newMessages.length - 1]
        if (lastMsg && lastMsg.streaming) {
          lastMsg.streaming = false
        }
        return newMessages
      })
      setIsStreaming(false)
    } else if (data.type === 'system') {
      console.log('System message:', data.content)
    } else if (data.type === 'log') {
      console.log('Log:', data.content)
    }
  }

  const sendMessage = () => {
    if (!input.trim() || !ws || ws.readyState !== WebSocket.OPEN) {
      console.log('Cannot send:', { input: input.trim(), ws: !!ws, readyState: ws?.readyState })
      return
    }

    const userMessage = {
      sender: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsStreaming(true)

    const payload = {
      type: 'chat',
      content: input,
      agent: agentName
    }
    
    console.log('Sending:', payload)
    ws.send(JSON.stringify(payload))

    setInput('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="agent-chat glass">
      <div className="chat-header">
        <h2 className="chat-title">Chat with {agentName}</h2>
        {uploadedFile && (
          <span className="uploaded-indicator">File: {uploadedFile}</span>
        )}
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <p>Start a conversation with {agentName}</p>
            <p className="hint">Try: "Analyze my campaign" or "Give me keyword suggestions"</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender} slide-in`}>
            <div className="message-avatar">
              {msg.sender === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-text">{msg.content}</div>
              {msg.streaming && <span className="streaming-cursor">▊</span>}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isStreaming}
          rows={3}
        />
        <button 
          className="send-button"
          onClick={sendMessage}
          disabled={isStreaming || !input.trim()}
        >
          {isStreaming ? '⏳' : '🚀'} Send
        </button>
      </div>
    </div>
  )
}

export default AgentChat
