package com.example.springboot_backend;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.File;
import java.io.FileWriter;
import java.nio.file.Path;
import static org.junit.jupiter.api.Assertions.*;

public class MavenToGradleMigratorTest {
    @Test
    void testDetectMavenProject(@TempDir Path tempDir) throws Exception {
        // Create a pom.xml to simulate a Maven project
        File pomFile = new File(tempDir.toFile(), "pom.xml");
        try (FileWriter writer = new FileWriter(pomFile)) {
            writer.write("<project></project>");
        }
        // Do not actually run gradle init in this test (would require gradle installed)
        MigrationResult result = MavenToGradleMigrator.migrateIfMaven(tempDir.toFile());
        // Accept either migration success or failure, but must detect Maven
        assertTrue(result.wasMaven);
        assertNotNull(result.message);
    }

    @Test
    void testDetectNonMavenProject(@TempDir Path tempDir) {
        MigrationResult result = MavenToGradleMigrator.migrateIfMaven(tempDir.toFile());
        assertFalse(result.wasMaven);
        assertFalse(result.migrationSuccess);
    }
} 