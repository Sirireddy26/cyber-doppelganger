package com.cyberdoppelganger.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class DatabaseHealthService {

    private static final Logger logger = LoggerFactory.getLogger(DatabaseHealthService.class);

    private final DataSource dataSource;

    public DatabaseHealthService(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    /**
     * Actively tests the database connection without exposing credentials.
     * Never hard-codes health.
     */
    public Map<String, String> checkDatabaseHealth() {
        Map<String, String> status = new LinkedHashMap<>();

        try (Connection connection = dataSource.getConnection()) {
            boolean valid = connection.isValid(2);
            if (valid) {
                DatabaseMetaData meta = connection.getMetaData();
                String productName = meta.getDatabaseProductName();
                status.put("database", "UP");
                status.put("database_type", productName);
            } else {
                status.put("database", "DOWN");
                status.put("database_type", "UNKNOWN");
                status.put("error", "Connection validation failed");
            }
        } catch (Exception e) {
            logger.warn("Database health check failed: {}", e.getMessage());
            status.put("database", "DOWN");
            status.put("database_type", "UNREACHABLE");
            status.put("error", "Database connection could not be established");
        }

        return status;
    }
}
