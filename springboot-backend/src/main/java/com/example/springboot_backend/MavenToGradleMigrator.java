package com.example.springboot_backend;

import java.io.File;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;

public class MavenToGradleMigrator {
    private static final Logger logger = LoggerFactory.getLogger(MavenToGradleMigrator.class);

    public static MigrationResult migrateIfMaven(File repoDir) {
        File pomFile = new File(repoDir, "pom.xml");
        if (!pomFile.exists()) {
            logger.info("No pom.xml found in {}. Not a Maven project.", repoDir.getPath());
            return new MigrationResult(false, false, "Not a Maven project");
        }
        logger.info("Detected Maven project at {}. Attempting migration to Gradle...", repoDir.getPath());
        try {
            ProcessBuilder pb = new ProcessBuilder("gradle", "init", "--type", "pom");
            pb.directory(repoDir);
            pb.redirectErrorStream(true);
            Process process = pb.start();
            int exitCode = process.waitFor();
            File gradleFile = new File(repoDir, "build.gradle");
            if (exitCode == 0 && gradleFile.exists()) {
                logger.info("Migration to Gradle successful for {}", repoDir.getPath());
                return new MigrationResult(true, true, "Migration successful");
            } else {
                logger.error("Migration to Gradle failed for {}. Exit code: {}", repoDir.getPath(), exitCode);
                return new MigrationResult(true, false, "Migration failed. Exit code: " + exitCode);
            }
        } catch (IOException | InterruptedException e) {
            logger.error("Exception during migration for {}", repoDir.getPath(), e);
            return new MigrationResult(true, false, "Migration failed: " + e.getMessage());
        }
    }
} 