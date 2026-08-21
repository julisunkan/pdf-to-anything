---
name: Flask background jobs
description: Context requirement for asynchronous conversion workers
---

Background conversion workers must capture the Flask application object from the request and enter `app.app_context()` before calling conversion or database services.

**Why:** Flask's `current_app` and SQLAlchemy session access are context-local; starting a bare thread can accept a job successfully while the worker crashes before doing any work.

**How to apply:** Use an app-aware worker wrapper for every asynchronous conversion entry point, including browser and API routes.