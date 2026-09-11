# Data Directory

This directory stores persistent SQLite database files for CareerBridge AI.

- `careerbridge.db`: SQLite database storing user sessions, message histories, and extracted user profile context.
- The database schema is initialized automatically upon backend startup.
- In-memory fallback is automatically engaged if file persistence is not writable.
