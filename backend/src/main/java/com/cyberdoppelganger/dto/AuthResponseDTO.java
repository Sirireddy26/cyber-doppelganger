package com.cyberdoppelganger.dto;

public class AuthResponseDTO {

    private String token;
    private String type = "Bearer";
    private String username;
    private String email;
    private String role;
    private long expiresInMs;

    public AuthResponseDTO() {}

    public AuthResponseDTO(String token, String username, String email, String role, long expiresInMs) {
        this.token = token;
        this.type = "Bearer";
        this.username = username;
        this.email = email;
        this.role = role;
        this.expiresInMs = expiresInMs;
    }

    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public long getExpiresInMs() { return expiresInMs; }
    public void setExpiresInMs(long expiresInMs) { this.expiresInMs = expiresInMs; }
}
