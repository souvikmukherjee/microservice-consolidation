package com.example.springboot_backend;

import java.io.File;
import java.io.IOException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ResultSerializer {
    private static final Logger logger = LoggerFactory.getLogger(ResultSerializer.class);

    public static void serializeToJson(AnalysisResult result, File outFile) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            mapper.writerWithDefaultPrettyPrinter().writeValue(outFile, result);
        } catch (IOException e) {
            logger.error("Failed to write analysis result", e);
        }
    }
} 