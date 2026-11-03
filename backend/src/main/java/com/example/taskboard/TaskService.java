package com.example.taskboard;

import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.stereotype.Service;

@Service
public class TaskService {
    private final ConcurrentMap<Long, Task> tasks = new ConcurrentHashMap<>();
    private final AtomicLong ids = new AtomicLong();

    public TaskService() {
        create("Learn Jenkins Pipeline");
        create("Build Spring Boot API");
        create("Connect ReactJS frontend");
    }

    public List<Task> list() {
        return tasks.values().stream()
                .sorted(Comparator.comparingLong(Task::id))
                .toList();
    }

    public Task create(String title) {
        long id = ids.incrementAndGet();
        Task task = new Task(id, title.trim(), false);
        tasks.put(id, task);
        return task;
    }

    public Optional<Task> toggle(long id) {
        return Optional.ofNullable(tasks.computeIfPresent(id,
                (ignored, old) -> new Task(old.id(), old.title(), !old.completed())));
    }

    public boolean delete(long id) {
        return tasks.remove(id) != null;
    }
}
