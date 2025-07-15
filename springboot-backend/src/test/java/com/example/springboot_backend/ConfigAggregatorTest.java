package com.example.springboot_backend;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.File;
import java.io.FileWriter;
import java.nio.file.Path;
import java.util.Map;
import static org.junit.jupiter.api.Assertions.*;

public class ConfigAggregatorTest {
    @Test
    void testAggregateConfig_propertiesAndYaml(@TempDir Path tempDir) throws Exception {
        // Create a sample .properties file
        File propFile = new File(tempDir.toFile(), "application.properties");
        try (FileWriter writer = new FileWriter(propFile)) {
            writer.write("key1=value1\nkey2=value2\n");
        }
        // Create a sample .yml file
        File yamlFile = new File(tempDir.toFile(), "application.yml");
        try (FileWriter writer = new FileWriter(yamlFile)) {
            writer.write("key3: value3\nkey4: value4\n");
        }
        Map<String, Object> config = ConfigAggregator.aggregateConfig(tempDir.toFile());
        assertEquals("value1", config.get("key1"));
        assertEquals("value2", config.get("key2"));
        assertEquals("value3", config.get("key3"));
        assertEquals("value4", config.get("key4"));
    }
} 