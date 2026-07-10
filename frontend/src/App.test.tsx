import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import * as api from './api'
import type { Task } from './types'

vi.mock('./api')

const mockedApi = vi.mocked(api)

function makeTask(overrides: Partial<Task> = {}): Task {
  return {
    id: 't1',
    title: 'Write CLAUDE.md',
    description: '',
    status: 'todo',
    priority: 'medium',
    created_at: '2026-07-09T00:00:00Z',
    updated_at: '2026-07-09T00:00:00Z',
    ...overrides,
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedApi.listTasks.mockResolvedValue([])
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ status: 'ok' }),
  }) as unknown as typeof fetch
})

describe('App', () => {
  it('renders the task list from listTasks on mount', async () => {
    mockedApi.listTasks.mockResolvedValue([makeTask({ title: 'Ship phase 03' })])

    render(<App />)

    expect(await screen.findByText('Ship phase 03')).toBeInTheDocument()
  })

  it('shows a task count summary once tasks load, counting done separately', async () => {
    mockedApi.listTasks.mockResolvedValue([
      makeTask({ id: 't1', status: 'done' }),
      makeTask({ id: 't2', status: 'todo' }),
      makeTask({ id: 't3', status: 'doing' }),
    ])

    render(<App />)

    expect(await screen.findByText('3 tasks, 1 done')).toBeInTheDocument()
  })

  it('shows no summary when there are no tasks', async () => {
    mockedApi.listTasks.mockResolvedValue([])

    render(<App />)
    await screen.findByText('No tasks yet.')

    expect(screen.queryByText(/done$/)).not.toBeInTheDocument()
  })

  it('shows an error message instead of clearing the list when a refresh fails', async () => {
    const user = userEvent.setup()
    mockedApi.listTasks.mockResolvedValueOnce([makeTask({ title: 'Write CLAUDE.md' })])
    mockedApi.updateTask.mockResolvedValue(makeTask({ status: 'doing' }))

    render(<App />)
    await screen.findByText('Write CLAUDE.md')

    mockedApi.listTasks.mockRejectedValueOnce(new Error('network error'))
    await user.selectOptions(screen.getByRole('combobox'), 'doing')

    expect(await screen.findByText("Couldn't load tasks — try refreshing.")).toBeInTheDocument()
    // The stale-but-real task list is preserved rather than being wiped to empty.
    expect(screen.getByText('Write CLAUDE.md')).toBeInTheDocument()
    expect(screen.queryByText('No tasks yet.')).not.toBeInTheDocument()
  })

  it('ignores an out-of-order stale response so it cannot clobber fresher state', async () => {
    const user = userEvent.setup()
    const staleTask = makeTask({ id: 'stale', title: 'Stale task' })
    const freshTask = makeTask({ id: 'fresh', title: 'Fresh task' })

    let resolveFirst: (tasks: Task[]) => void = () => {}
    let resolveSecond: (tasks: Task[]) => void = () => {}
    const firstCall = new Promise<Task[]>((resolve) => {
      resolveFirst = resolve
    })
    const secondCall = new Promise<Task[]>((resolve) => {
      resolveSecond = resolve
    })

    mockedApi.listTasks
      .mockImplementationOnce(() => firstCall) // initial mount call
      .mockImplementationOnce(() => secondCall) // triggered by handleAddTask
    mockedApi.createTask.mockResolvedValue(freshTask)

    render(<App />)
    await waitFor(() => expect(mockedApi.listTasks).toHaveBeenCalledTimes(1))

    await user.type(screen.getByPlaceholderText('New task title'), 'Fresh task')
    await user.click(screen.getByRole('button', { name: 'Add' }))
    await waitFor(() => expect(mockedApi.listTasks).toHaveBeenCalledTimes(2))

    // Second (fresher) request resolves before the first (stale) request.
    resolveSecond([freshTask])
    await screen.findByText('Fresh task')

    resolveFirst([staleTask])
    await waitFor(() => expect(mockedApi.listTasks).toHaveBeenCalledTimes(2))

    expect(screen.queryByText('Stale task')).not.toBeInTheDocument()
    expect(screen.getByText('Fresh task')).toBeInTheDocument()
  })

  it('shows unreachable when the health check fails', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: false, status: 500 }) as unknown as typeof fetch

    render(<App />)

    expect(await screen.findByText('unreachable')).toBeInTheDocument()
  })

  it('submitting the add-task form creates a task with the trimmed title', async () => {
    const user = userEvent.setup()
    mockedApi.createTask.mockResolvedValue(makeTask())

    render(<App />)

    await user.type(screen.getByPlaceholderText('New task title'), '  New task  ')
    await user.click(screen.getByRole('button', { name: 'Add' }))

    await waitFor(() => expect(mockedApi.createTask).toHaveBeenCalledWith('New task'))
    await waitFor(() => expect(mockedApi.listTasks).toHaveBeenCalledTimes(2)) // initial + refresh after add
  })

  it('changing the status select calls updateTask with the new status', async () => {
    const user = userEvent.setup()
    mockedApi.listTasks.mockResolvedValue([makeTask()])
    mockedApi.updateTask.mockResolvedValue(makeTask({ status: 'doing' }))

    render(<App />)
    await screen.findByText('Write CLAUDE.md')

    await user.selectOptions(screen.getByRole('combobox'), 'doing')

    expect(mockedApi.updateTask).toHaveBeenCalledWith('t1', { status: 'doing' })
  })

  it('clicking "Suggest priority" shows loading then the suggestion', async () => {
    const user = userEvent.setup()
    mockedApi.listTasks.mockResolvedValue([makeTask()])
    mockedApi.triageTask.mockResolvedValue({ priority: 'high', rationale: 'It is urgent.' })

    render(<App />)
    await screen.findByText('Write CLAUDE.md')

    await user.click(screen.getByRole('button', { name: 'Suggest priority' }))

    expect(await screen.findByText(/Suggested:/)).toBeInTheDocument()
    expect(screen.getByText(/It is urgent\./)).toBeInTheDocument()
  })

  it('asks for confirmation before deleting, and deletes when confirmed', async () => {
    const user = userEvent.setup()
    mockedApi.listTasks.mockResolvedValue([makeTask({ title: 'Write CLAUDE.md' })])
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    render(<App />)
    await screen.findByText('Write CLAUDE.md')

    await user.click(screen.getByRole('button', { name: 'Delete' }))

    expect(window.confirm).toHaveBeenCalledWith('Delete "Write CLAUDE.md"?')
    await waitFor(() => expect(mockedApi.deleteTask).toHaveBeenCalledWith('t1'))
  })

  it('does not delete when the confirmation is cancelled', async () => {
    const user = userEvent.setup()
    mockedApi.listTasks.mockResolvedValue([makeTask({ title: 'Write CLAUDE.md' })])
    vi.spyOn(window, 'confirm').mockReturnValue(false)

    render(<App />)
    await screen.findByText('Write CLAUDE.md')

    await user.click(screen.getByRole('button', { name: 'Delete' }))

    expect(window.confirm).toHaveBeenCalled()
    expect(mockedApi.deleteTask).not.toHaveBeenCalled()
  })
})
