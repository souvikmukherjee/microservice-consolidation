package com.example.springboot_backend;

public class MigrationResult {
    public boolean wasMaven;
    public boolean migrationSuccess;
    public String message;

    public MigrationResult(boolean wasMaven, boolean migrationSuccess, String message) {
        this.wasMaven = wasMaven;
        this.migrationSuccess = migrationSuccess;
        this.message = message;
    }
} 