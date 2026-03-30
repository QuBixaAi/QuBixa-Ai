import React, { useEffect, useRef } from 'react'
import './PredictionGraph.css'

function PredictionGraph({ predictions }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    if (!predictions || !predictions.time_series || predictions.time_series.length === 0) {
      return
    }

    drawGraph()
  }, [predictions])

  const drawGraph = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    const data = predictions.time_series
    const maxClicks = Math.max(...data.map(d => d.clicks))
    const maxCost = Math.max(...data.map(d => d.cost))
    const maxConversions = Math.max(...data.map(d => d.conversions))

    const padding = 40
    const graphWidth = width - padding * 2
    const graphHeight = height - padding * 2
    const stepX = graphWidth / (data.length - 1)

    // Draw grid
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.1)'
    ctx.lineWidth = 1
    for (let i = 0; i <= 5; i++) {
      const y = padding + (graphHeight / 5) * i
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(width - padding, y)
      ctx.stroke()
    }

    // Draw clicks line
    ctx.strokeStyle = '#6366f1'
    ctx.lineWidth = 3
    ctx.beginPath()
    data.forEach((point, index) => {
      const x = padding + stepX * index
      const y = padding + graphHeight - (point.clicks / maxClicks) * graphHeight
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })
    ctx.stroke()

    // Draw conversions line
    ctx.strokeStyle = '#10b981'
    ctx.lineWidth = 3
    ctx.beginPath()
    data.forEach((point, index) => {
      const x = padding + stepX * index
      const y = padding + graphHeight - (point.conversions / maxConversions) * graphHeight
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })
    ctx.stroke()

    // Draw cost line
    ctx.strokeStyle = '#f59e0b'
    ctx.lineWidth = 3
    ctx.beginPath()
    data.forEach((point, index) => {
      const x = padding + stepX * index
      const y = padding + graphHeight - (point.cost / maxCost) * graphHeight
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })
    ctx.stroke()

    // Draw points
    data.forEach((point, index) => {
      const x = padding + stepX * index
      
      // Clicks point
      const yClicks = padding + graphHeight - (point.clicks / maxClicks) * graphHeight
      ctx.fillStyle = '#6366f1'
      ctx.beginPath()
      ctx.arc(x, yClicks, 5, 0, Math.PI * 2)
      ctx.fill()

      // Conversions point
      const yConversions = padding + graphHeight - (point.conversions / maxConversions) * graphHeight
      ctx.fillStyle = '#10b981'
      ctx.beginPath()
      ctx.arc(x, yConversions, 5, 0, Math.PI * 2)
      ctx.fill()

      // Day labels
      ctx.fillStyle = '#94a3b8'
      ctx.font = '12px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(`Day ${point.day}`, x, height - 10)
    })

    // Legend
    const legendY = 20
    ctx.font = '14px sans-serif'
    ctx.textAlign = 'left'
    
    ctx.fillStyle = '#6366f1'
    ctx.fillRect(width - 150, legendY, 20, 3)
    ctx.fillStyle = '#f8fafc'
    ctx.fillText('Clicks', width - 125, legendY + 5)
    
    ctx.fillStyle = '#10b981'
    ctx.fillRect(width - 150, legendY + 20, 20, 3)
    ctx.fillStyle = '#f8fafc'
    ctx.fillText('Conversions', width - 125, legendY + 25)
    
    ctx.fillStyle = '#f59e0b'
    ctx.fillRect(width - 150, legendY + 40, 20, 3)
    ctx.fillStyle = '#f8fafc'
    ctx.fillText('Cost', width - 125, legendY + 45)
  }

  if (!predictions || !predictions.time_series) {
    return (
      <div className="prediction-graph glass">
        <h3 className="graph-title">7-Day Predictions</h3>
        <div className="graph-empty">
          <p>No prediction data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="prediction-graph glass">
      <h3 className="graph-title">7-Day Performance Predictions</h3>
      <div className="graph-stats">
        <div className="stat-item">
          <span className="stat-label">Predicted Clicks</span>
          <span className="stat-value">{predictions.predicted_clicks?.toLocaleString()}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Predicted Cost</span>
          <span className="stat-value">${predictions.predicted_cost?.toLocaleString()}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Predicted ROI</span>
          <span className="stat-value success">{predictions.predicted_roi}%</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Confidence</span>
          <span className="stat-value">{(predictions.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>
      <canvas 
        ref={canvasRef} 
        width={600} 
        height={300}
        className="prediction-canvas"
      />
    </div>
  )
}

export default PredictionGraph
