import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

// 1. Verify DOM element exists
const rootElement = document.getElementById('root')
console.log('Root element:', rootElement) // Should show <div> in console

// 2. Error handling for missing element
if (!rootElement) {
  throw new Error("Root element '#root' not found")
}

// 3. Create root correctly
const root = ReactDOM.createRoot(rootElement)

// 4. Render application
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
