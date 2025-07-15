package com.example.springboot_backend;

import java.io.File;
import java.util.Map;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RepoAnalysisModule {
    private static final Logger logger = LoggerFactory.getLogger(RepoAnalysisModule.class);

    public static void main(String[] args) {
        if (args.length == 0) {
            logger.info("Usage: java RepoAnalysisModule <repo-folder>");
            return;
        }
        String repoPath = args[0];
        if (!repoPath.startsWith("./repos")) {
            logger.error("Error: Only repositories inside ./repos can be analyzed.");
            return;
        }
        File repoDir = new File(repoPath);
        if (!repoDir.exists() || !repoDir.isDirectory()) {
            logger.error("Error: Provided path does not exist or is not a directory.");
            return;
        }
        // 1. Aggregate configuration
        Map<String, Object> config = ConfigAggregator.aggregateConfig(repoDir);
        // 2. Extract REST endpoints
        List<RestEndpoint> endpoints = RestControllerAnalyzer.extractEndpoints(repoDir);
        // 3. Detect Maven and migrate to Gradle
        MigrationResult migrationResult = MavenToGradleMigrator.migrateIfMaven(repoDir);
        // 4. Output results
        AnalysisResult result = new AnalysisResult(config, endpoints, migrationResult);
        ResultSerializer.serializeToJson(result, new File(repoDir, "analysis_result.json"));
        logger.info("Analysis complete. Results written to analysis_result.json");
    }
} 