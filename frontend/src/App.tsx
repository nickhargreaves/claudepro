import { useEffect, useRef, useState } from 'react'
import './App.css'
import { createTask, deleteTask, listTasks, triageTask, updateTask } from './api'
import type { Task, TaskStatus, TriageSuggestion } from './types'

type HealthStatus = 'checking' | 'ok' | 'unreachable'

function App() {
  const [health, setHealth] = useState<HealthStatus>('checking')
  const [tasks, setTasks] = useState<Task[]>([])
  const [tasksError, setTasksError] = useState(false)
  const [title, setTitle] = useState('')
  const [suggestions, setSuggestions] = useState<Record<string, TriageSuggestion | 'loading' | 'error'>>({})
  const latestRequestId = useRef(0)

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((data: { status: string }) => setHealth(data.status === 'ok' ? 'ok' : 'unreachable'))
      .catch(() => setHealth('unreachable'))

    refreshTasks()
  }, [])

  function refreshTasks() {
    const requestId = ++latestRequestId.current
    listTasks()
      .then((result) => {
        if (requestId !== latestRequestId.current) return
        setTasks(result)
        setTasksError(false)
      })
      .catch(() => {
        if (requestId !== latestRequestId.current) return
        setTasksError(true)
      })
  }

  async function handleAddTask(event: React.FormEvent) {
    event.preventDefault()
    if (!title.trim()) return
    await createTask(title.trim())
    setTitle('')
    refreshTasks()
  }

  async function handleStatusChange(task: Task, status: TaskStatus) {
    await updateTask(task.id, { status })
    refreshTasks()
  }

  async function handleDelete(task: Task) {
    if (!window.confirm(`Delete "${task.title}"?`)) return
    await deleteTask(task.id)
    refreshTasks()
  }

  async function handleTriage(task: Task) {
    setSuggestions((prev) => ({ ...prev, [task.id]: 'loading' }))
    try {
      const suggestion = await triageTask(task.id)
      setSuggestions((prev) => ({ ...prev, [task.id]: suggestion }))
    } catch {
      setSuggestions((prev) => ({ ...prev, [task.id]: 'error' }))
    }
  }

  return (
    <main className="shell">
      <h1>TaskFlow</h1>
      <p>
        Backend status: <strong className={`status status-${health}`}>{health}</strong>
      </p>
      {tasksError && <p className="task-error">Couldn't load tasks — try refreshing.</p>}
      {!tasksError && tasks.length > 0 && (
        <p className="task-summary">
          {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'},{' '}
          {tasks.filter((t) => t.status === 'done').length} done
        </p>
      )}

      <form onSubmit={handleAddTask} className="add-task">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New task title"
        />
        <button type="submit">Add</button>
      </form>

      <ul className="task-list">
        {tasks.map((task) => {
          const suggestion = suggestions[task.id]
          return (
            <li key={task.id} className="task-row-wrap">
              <div className="task-row">
                <span className="task-title">{task.title}</span>
                <span className="task-priority">{task.priority}</span>
                <select
                  value={task.status}
                  onChange={(e) => handleStatusChange(task, e.target.value as TaskStatus)}
                >
                  <option value="todo">todo</option>
                  <option value="doing">doing</option>
                  <option value="done">done</option>
                </select>
                <button type="button" onClick={() => handleTriage(task)}>
                  Suggest priority
                </button>
                <button type="button" onClick={() => handleDelete(task)}>
                  Delete
                </button>
              </div>
              {suggestion === 'loading' && <p className="task-suggestion">Asking Claude…</p>}
              {suggestion === 'error' && (
                <p className="task-suggestion task-suggestion-error">Triage failed — try again.</p>
              )}
              {suggestion && suggestion !== 'loading' && suggestion !== 'error' && (
                <p className="task-suggestion">
                  Suggested: <strong>{suggestion.priority}</strong> — {suggestion.rationale}
                </p>
              )}
            </li>
          )
        })}
        {tasks.length === 0 && <li className="task-empty">No tasks yet.</li>}
      </ul>
    </main>
  )
}

export default App
