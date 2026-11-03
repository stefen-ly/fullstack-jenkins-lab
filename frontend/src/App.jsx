import React, { useEffect, useState } from 'react';
import { normalizeTitle, taskStats } from './taskHelpers.js';

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  async function api(path, options = {}) {
    const response = await fetch('/api' + path, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
    });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    if (response.status === 204) return null;
    return response.json();
  }

  async function refresh() {
    try {
      setTasks(await api('/tasks'));
      setError('');
    } catch (e) { setError('Cannot connect to the Spring Boot API.'); }
  }

  useEffect(() => { refresh(); }, []);

  async function addTask(event) {
    event.preventDefault();
    const clean = normalizeTitle(title);
    if (!clean || clean.length > 120) return;
    setBusy(true); setNotice('');
    try {
      await api('/tasks', { method: 'POST', body: JSON.stringify({ title: clean }) });
      setTitle(''); await refresh(); setNotice('Task created');
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  async function toggleTask(id) {
    setBusy(true); setNotice('');
    try { await api(`/tasks/${id}/toggle`, { method: 'PATCH' }); await refresh(); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  async function removeTask(id) {
    setBusy(true); setNotice('');
    try { await api(`/tasks/${id}`, { method: 'DELETE' }); await refresh(); setNotice('Task removed'); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  const stats = taskStats(tasks);
  const percent = stats.total === 0 ? 0 : Math.round((stats.complete / stats.total) * 100);

  return (
    <div className="page">
      <header className="topbar">
        <div className="logo"><span className="logo-mark">↗</span> DEPLOY<span className="accent">LAB</span></div>
        <span className="build-label"><span className="dot" /> Jenkins CI/CD Demo</span>
      </header>
      <main className="main">
        <section className="intro">
          <div className="eyebrow">SPRING BOOT × REACT × JENKINS</div>
          <h1>Build something.<br /><span>Ship with confidence.</span></h1>
          <p>A tiny task manager powering a full-stack CI/CD lab. Add tasks, mark them done, then watch Jenkins test and deploy both services.</p>
        </section>
        <section className="workspace">
          <div className="section-heading"><div><div className="eyebrow">PROJECT BOARD</div><h2>My tasks</h2></div><span className="count">{stats.total} tasks</span></div>
          <div className="stats"><div><strong>{stats.total}</strong><span>Total</span></div><div><strong>{stats.complete}</strong><span>Completed</span></div><div><strong>{stats.remaining}</strong><span>Remaining</span></div></div>
          <div className="progress-meta"><span>Progress</span><strong>{percent}%</strong></div>
          <div className="progress"><div style={{ width: percent + '%' }} /></div>
          <form onSubmit={addTask} className="addform"><input aria-label="New task" maxLength={120} placeholder="What needs to be done?" value={title} onChange={(e) => setTitle(e.target.value)} /><button disabled={busy || !normalizeTitle(title)} type="submit">+ Add task</button></form>
          {error && <div className="error" role="alert">{error}</div>}
          {notice && <div className="notice" role="status">{notice}</div>}
          <div className="task-list">
            {tasks.map((task) => <div className="task" key={task.id}>
                <button disabled={busy} className={'check ' + (task.completed ? 'checked' : '')} onClick={() => toggleTask(task.id)} aria-label={'Toggle ' + task.title}>{task.completed ? '✓' : ''}</button>
                <span className={task.completed ? 'done' : ''}>{task.title}</span>
                <button disabled={busy} className="remove" onClick={() => removeTask(task.id)} aria-label={'Remove ' + task.title}>×</button>
              </div>)}
            {tasks.length === 0 && !error && <div className="empty">No tasks yet. Add one above to get started.</div>}
          </div>
        </section>
        <footer>Made for learning • Git → Jenkins → Docker → Email + Telegram</footer>
      </main>
    </div>
  );
}
