package com.example.springboot_backend;

public class RestEndpoint {
    public String className;
    public String methodName;
    public String httpMethod;
    public String path;

    public RestEndpoint(String className, String methodName, String httpMethod, String path) {
        this.className = className;
        this.methodName = methodName;
        this.httpMethod = httpMethod;
        this.path = path;
    }
} 