package com.cyberdoppelganger.service;

import com.cyberdoppelganger.dto.AuthResponseDTO;
import com.cyberdoppelganger.dto.LoginRequestDTO;
import com.cyberdoppelganger.dto.RegisterRequestDTO;
import com.cyberdoppelganger.dto.UserDTO;
import com.cyberdoppelganger.entity.User;
import com.cyberdoppelganger.exception.ValidationException;
import com.cyberdoppelganger.repository.UserRepository;
import com.cyberdoppelganger.security.JwtTokenProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private static final Logger logger = LoggerFactory.getLogger(AuthService.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;
    private final AuditService auditService;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtTokenProvider tokenProvider,
            AuditService auditService
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.tokenProvider = tokenProvider;
        this.auditService = auditService;
    }

    @Transactional
    public UserDTO register(RegisterRequestDTO dto) {
        String username = dto.getUsername().trim();
        String email = dto.getEmail().trim().toLowerCase();

        if (userRepository.existsByUsername(username)) {
            throw new ValidationException("Username '" + username + "' is already taken");
        }
        if (userRepository.existsByEmail(email)) {
            throw new ValidationException("Email '" + email + "' is already registered");
        }

        String passwordHash = passwordEncoder.encode(dto.getPassword());
        User user = new User(username, email, passwordHash, "ROLE_USER");
        User saved = userRepository.save(user);

        auditService.record(saved.getId(), "USER_REGISTERED", "USER", saved.getId().toString(), "SUCCESS", "{}");
        logger.info("New user registered successfully: [{}]", username);

        return new UserDTO(saved.getId(), saved.getUsername(), saved.getEmail(), saved.getRole(), saved.getCreatedAt(), saved.isEnabled());
    }

    @Transactional(readOnly = true)
    public AuthResponseDTO login(LoginRequestDTO dto) {
        String username = dto.getUsername().trim();
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new ValidationException("Invalid username or password"));

        if (!passwordEncoder.matches(dto.getPassword(), user.getPasswordHash())) {
            auditService.record(user.getId(), "LOGIN_FAILED", "USER", user.getId().toString(), "FAILURE", "{\"reason\":\"invalid_credentials\"}");
            throw new ValidationException("Invalid username or password");
        }

        String token = tokenProvider.generateToken(user.getUsername(), user.getRole());
        auditService.record(user.getId(), "LOGIN_SUCCESS", "USER", user.getId().toString(), "SUCCESS", "{}");
        logger.info("User [{}] logged in successfully", username);

        return new AuthResponseDTO(token, user.getUsername(), user.getEmail(), user.getRole(), tokenProvider.getExpirationMs());
    }
}
