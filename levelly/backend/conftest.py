"""
LEVELLY — Pytest Configuration
Sets up the test database environment.
"""
import pytest
import os

# Explicit test environment with isolated in-memory SQLite
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-32-characters-min"
os.environ["JWT_SECRET"] = "test-jwt-secret-32-characters-min"
os.environ["GROQ_API_KEY"] = ""  # No AI calls in tests
