package com.example.springboot_backend;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.File;
import java.util.Map;
import java.util.HashMap;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.IOException;
import java.util.Properties;
import org.yaml.snakeyaml.Yaml;
import java.util.List;
import java.util.ArrayList;

public class ConfigAggregator {
    private static final Logger logger = LoggerFactory.getLogger(ConfigAggregator.class);

    public static Map<String, Object> aggregateConfig(File repoDir) {
        Map<String, Object> aggregatedConfig = new HashMap<>();
        List<File> configFiles = new ArrayList<>();
        findConfigFiles(repoDir, configFiles);
        for (File file : configFiles) {
            if (file.getName().endsWith(".properties")) {
                Properties props = new Properties();
                try (FileInputStream fis = new FileInputStream(file)) {
                    props.load(fis);
                    for (String key : props.stringPropertyNames()) {
                        aggregatedConfig.put(key, props.getProperty(key));
                    }
                    logger.info("Loaded properties from {}", file.getPath());
                } catch (IOException e) {
                    logger.error("Failed to load properties file: {}", file.getPath(), e);
                }
            } else if (file.getName().endsWith(".yml") || file.getName().endsWith(".yaml")) {
                Yaml yaml = new Yaml();
                try (InputStream input = new FileInputStream(file)) {
                    Iterable<Object> docs = yaml.loadAll(input);
                    for (Object data : docs) {
                        if (data instanceof Map) {
                            flattenYaml((Map<?, ?>) data, "", aggregatedConfig);
                        }
                    }
                    logger.info("Loaded YAML from {}", file.getPath());
                } catch (IOException e) {
                    logger.error("Failed to load YAML file: {}", file.getPath(), e);
                }
            }
        }
        return aggregatedConfig;
    }

    private static void findConfigFiles(File dir, List<File> configFiles) {
        if (dir == null || !dir.exists()) return;
        File[] files = dir.listFiles();
        if (files == null) return;
        for (File file : files) {
            if (file.isDirectory()) {
                findConfigFiles(file, configFiles);
            } else if (file.getName().endsWith(".properties") || file.getName().endsWith(".yml") || file.getName().endsWith(".yaml")) {
                configFiles.add(file);
            }
        }
    }

    // Helper to flatten nested YAML structures into dot-separated keys
    private static void flattenYaml(Map<?, ?> map, String prefix, Map<String, Object> out) {
        for (Map.Entry<?, ?> entry : map.entrySet()) {
            String key = prefix.isEmpty() ? entry.getKey().toString() : prefix + "." + entry.getKey().toString();
            Object value = entry.getValue();
            if (value instanceof Map) {
                flattenYaml((Map<?, ?>) value, key, out);
            } else {
                out.put(key, value == null ? null : value.toString());
            }
        }
    }
} 