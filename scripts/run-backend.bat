@echo off
cd /d "%~dp0\..\backend"
echo Starting Cyber Doppelganger Spring Boot Backend on http://localhost:8080...
.\mvnw.cmd spring-boot:run
