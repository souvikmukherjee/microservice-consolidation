package com.example.springboot_backend;

import java.io.File;
import java.util.List;
import java.util.ArrayList;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.AnnotationExpr;
import com.github.javaparser.ast.expr.NormalAnnotationExpr;
import com.github.javaparser.ast.expr.SingleMemberAnnotationExpr;
import com.github.javaparser.ast.expr.MemberValuePair;
import com.github.javaparser.utils.SourceRoot;
import java.nio.file.Paths;
import java.util.Optional;
import java.io.IOException;

public class RestControllerAnalyzer {
    private static final Logger logger = LoggerFactory.getLogger(RestControllerAnalyzer.class);

    public static List<RestEndpoint> extractEndpoints(File repoDir) {
        List<RestEndpoint> endpoints = new ArrayList<>();
        List<File> javaFiles = new ArrayList<>();
        findJavaFiles(repoDir, javaFiles);
        JavaParser parser = new JavaParser();
        for (File file : javaFiles) {
            try {
                Optional<CompilationUnit> cuOpt = parser.parse(file).getResult();
                if (!cuOpt.isPresent()) continue;
                CompilationUnit cu = cuOpt.get();
                cu.findAll(ClassOrInterfaceDeclaration.class).forEach(clazz -> {
                    boolean isRestController = clazz.getAnnotations().stream()
                        .anyMatch(a -> a.getNameAsString().equals("RestController"));
                    if (isRestController) {
                        String className = clazz.getNameAsString();
                        clazz.getMethods().forEach(method -> {
                            extractEndpointFromMethod(className, method, endpoints);
                        });
                        logger.info("Found @RestController: {}", className);
                    }
                });
            } catch (IOException e) {
                logger.error("Failed to parse Java file: {}", file.getPath(), e);
            }
        }
        return endpoints;
    }

    private static void findJavaFiles(File dir, List<File> javaFiles) {
        if (dir == null || !dir.exists()) return;
        File[] files = dir.listFiles();
        if (files == null) return;
        for (File file : files) {
            if (file.isDirectory()) {
                findJavaFiles(file, javaFiles);
            } else if (file.getName().endsWith(".java")) {
                javaFiles.add(file);
            }
        }
    }

    private static void extractEndpointFromMethod(String className, MethodDeclaration method, List<RestEndpoint> endpoints) {
        for (AnnotationExpr annotation : method.getAnnotations()) {
            String annotationName = annotation.getNameAsString();
            String httpMethod = null;
            String path = null;
            switch (annotationName) {
                case "GetMapping": httpMethod = "GET"; break;
                case "PostMapping": httpMethod = "POST"; break;
                case "PutMapping": httpMethod = "PUT"; break;
                case "DeleteMapping": httpMethod = "DELETE"; break;
                case "PatchMapping": httpMethod = "PATCH"; break;
                case "RequestMapping": httpMethod = "REQUEST"; break;
                default: continue;
            }
            // Extract path value
            if (annotation.isSingleMemberAnnotationExpr()) {
                path = ((SingleMemberAnnotationExpr) annotation).getMemberValue().toString().replaceAll("^\"|\"$", "");
            } else if (annotation.isNormalAnnotationExpr()) {
                for (MemberValuePair pair : ((NormalAnnotationExpr) annotation).getPairs()) {
                    if (pair.getNameAsString().equals("value") || pair.getNameAsString().equals("path")) {
                        path = pair.getValue().toString().replaceAll("^\"|\"$", "");
                    }
                    if (annotationName.equals("RequestMapping") && pair.getNameAsString().equals("method")) {
                        String methodValue = pair.getValue().toString();
                        if (methodValue.contains("GET")) httpMethod = "GET";
                        else if (methodValue.contains("POST")) httpMethod = "POST";
                        else if (methodValue.contains("PUT")) httpMethod = "PUT";
                        else if (methodValue.contains("DELETE")) httpMethod = "DELETE";
                        else if (methodValue.contains("PATCH")) httpMethod = "PATCH";
                    }
                }
            }
            if (path == null) path = "/";
            endpoints.add(new RestEndpoint(className, method.getNameAsString(), httpMethod, path));
        }
    }
} 