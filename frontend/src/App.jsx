import { useState, useEffect } from 'react'
import { classifyHeadline, getHeadlines, updateHeadline, deleteHeadline } from './services/api'
import HeadlineList from './components/HeadlineList'
import './index.css'
const API_URL = "http://localhost:8000"; 
function App() {
  const [input, setInput] = useState('')
  const [result, setResult] = useState(null)
  const [headlines, setHeadlines] = useState([])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const classification = await classifyHeadline(input)
      setResult(classification)
      setInput('')
      loadHeadlines()
    } catch (error) {
      console.error('Classification error:', error)
    }
  }

  const loadHeadlines = async () => {
    try {
      const data = await getHeadlines()
      setHeadlines(data)
    } catch (error) {
      console.error('Error loading headlines:', error)
    }
  }

  useEffect(() => {
    loadHeadlines()
  }, [])

  return (
    <div className="container">
      <h1>News Conspiracy Analyzer</h1>
      
      <form onSubmit={handleSubmit} className="analyzer-form">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter news headline..."
          required
        />
        <button type="submit">Analyze</button>
      </form>

      {result && (
        <div className="result-card">
          <h2>Analysis Result</h2>
          <p className={`score score-${Math.floor(result.score/20)}`}>
            Conspiracy Score: {result.score}%
          </p>
          <p>Category: {result.category}</p>
          {result.suspicious_words.length > 0 && (
            <div className="keywords">
              <span>Suspicious words: </span>
              {result.suspicious_words.join(', ')}
            </div>
          )}
        </div>
      )}

      <HeadlineList 
        headlines={headlines}
        onUpdate={updateHeadline}
        onDelete={deleteHeadline}
        refresh={loadHeadlines}
      />
    </div>
  )
}

export default App
