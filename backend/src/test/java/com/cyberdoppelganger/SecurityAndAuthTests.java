package com.cyberdoppelganger;

import com.cyberdoppelganger.entity.User;
import com.cyberdoppelganger.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;

import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class SecurityAndAuthTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void testUserRegistrationAndBCryptHashing() throws Exception {
        String registerPayload = """
        {
          "username": "alice",
          "email": "alice@example.com",
          "password": "Password123!"
        }
        """;

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(registerPayload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.username").value("alice"))
                .andExpect(jsonPath("$.email").value("alice@example.com"))
                .andExpect(jsonPath("$.role").value("ROLE_USER"));

        User savedUser = userRepository.findByUsername("alice").orElseThrow();
        // Passwords must NEVER be stored as plaintext
        assertNotEquals("Password123!", savedUser.getPasswordHash());
        assertTrue(passwordEncoder.matches("Password123!", savedUser.getPasswordHash()));
    }

    @Test
    void testDuplicateUsernameRejected() throws Exception {
        String payload = """
        {
          "username": "bob",
          "email": "bob1@example.com",
          "password": "Password123!"
        }
        """;
        mockMvc.perform(post("/api/auth/register").contentType(MediaType.APPLICATION_JSON).content(payload))
                .andExpect(status().isCreated());

        String duplicatePayload = """
        {
          "username": "bob",
          "email": "bob2@example.com",
          "password": "Password123!"
        }
        """;
        mockMvc.perform(post("/api/auth/register").contentType(MediaType.APPLICATION_JSON).content(duplicatePayload))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").value("Username 'bob' is already taken"));
    }

    @Test
    void testLoginSuccessReturnsJwtToken() throws Exception {
        // Register user
        String registerPayload = """
        {
          "username": "carol",
          "email": "carol@example.com",
          "password": "Password123!"
        }
        """;
        mockMvc.perform(post("/api/auth/register").contentType(MediaType.APPLICATION_JSON).content(registerPayload))
                .andExpect(status().isCreated());

        // Login
        String loginPayload = """
        {
          "username": "carol",
          "password": "Password123!"
        }
        """;
        mockMvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON).content(loginPayload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").isNotEmpty())
                .andExpect(jsonPath("$.type").value("Bearer"))
                .andExpect(jsonPath("$.username").value("carol"));
    }

    @Test
    void testLoginFailureWithWrongPassword() throws Exception {
        String registerPayload = """
        {
          "username": "dave",
          "email": "dave@example.com",
          "password": "CorrectPassword123"
        }
        """;
        mockMvc.perform(post("/api/auth/register").contentType(MediaType.APPLICATION_JSON).content(registerPayload))
                .andExpect(status().isCreated());

        String wrongLoginPayload = """
        {
          "username": "dave",
          "password": "WrongPassword!"
        }
        """;
        mockMvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON).content(wrongLoginPayload))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").value("Invalid username or password"));
    }
}
