package com.example.springboot_backend;

import java.util.Map;
import java.util.List;

public class AnalysisResult {
    public Map<String, Object> config;
    public List<RestEndpoint> endpoints;
    public MigrationResult migrationResult;

    public AnalysisResult(Map<String, Object> config, List<RestEndpoint> endpoints, MigrationResult migrationResult) {
        this.config = config;
        this.endpoints = endpoints;
        this.migrationResult = migrationResult;
    }
} 