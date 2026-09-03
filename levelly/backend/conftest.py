"""
LEVELLY — Pytest Configuration
Sets up the test database environment.
"""
import pytest
import os

# Use SQLite for tests — no PostgreSQL required
os.environ["DATABASE_URL"] = "sqlite:///./test_levelly.db"
os.environ["SECRET_KEY"] = "test-secret-key-32-characters-min"
os.environ["JWT_SECRET"] = "test-jwt-secret-32-characters-min"
os.environ["GROQ_API_KEY"] = ""  # No AI calls in tests
