package com.example.taskboard;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class TaskServiceTest {
    @Test
    void createListToggleDelete() {
        TaskService service = new TaskService();
        Task created = service.create("  Practice Jenkins CI/CD  ");
        assertEquals("Practice Jenkins CI/CD", created.title());
        assertFalse(created.completed());
        assertTrue(service.list().stream().anyMatch(t -> t.id() == created.id()));

        Task toggled = service.toggle(created.id()).orElseThrow();
        assertTrue(toggled.completed());
        assertTrue(service.delete(created.id()));
        assertTrue(service.toggle(created.id()).isEmpty());
        assertFalse(service.delete(created.id()));
    }
}
