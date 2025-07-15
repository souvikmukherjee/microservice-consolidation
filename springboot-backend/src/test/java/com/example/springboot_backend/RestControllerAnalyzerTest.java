package com.example.springboot_backend;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.File;
import java.io.FileWriter;
import java.nio.file.Path;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

public class RestControllerAnalyzerTest {
    @Test
    void testExtractEndpoints_simpleController(@TempDir Path tempDir) throws Exception {
        // Create a sample RestController Java file
        File javaFile = new File(tempDir.toFile(), "SampleController.java");
        try (FileWriter writer = new FileWriter(javaFile)) {
            writer.write("""
                import org.springframework.web.bind.annotation.*;
                @RestController
                public class SampleController {
                    @GetMapping("/hello")
                    public String hello() { return "hi"; }
                    @PostMapping("/submit")
                    public void submit() {}
                }
            """);
        }
        List<RestEndpoint> endpoints = RestControllerAnalyzer.extractEndpoints(tempDir.toFile());
        assertEquals(2, endpoints.size());
        assertTrue(endpoints.stream().anyMatch(e -> e.httpMethod.equals("GET") && e.path.equals("/hello")));
        assertTrue(endpoints.stream().anyMatch(e -> e.httpMethod.equals("POST") && e.path.equals("/submit")));
    }
} 