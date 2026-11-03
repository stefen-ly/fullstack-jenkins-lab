export function normalizeTitle(value) {
  return String(value ?? '').trim();
}

export function taskStats(tasks) {
  const complete = tasks.filter((task) => task.completed).length;
  return { total: tasks.length, complete, remaining: tasks.length - complete };
}
