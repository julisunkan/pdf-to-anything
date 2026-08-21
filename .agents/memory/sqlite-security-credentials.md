---
name: SQLite security credentials
description: Security storage choice for deployments that intentionally avoid Replit Secrets
---

The deployment uses a dedicated SQLite security-credentials table: the session secret is generated once and persisted, while the admin password is stored only as a salted hash.

**Why:** The user explicitly chose SQLite-backed persistence instead of Replit Secrets; keeping credentials separate from user-facing settings prevents the admin settings page from exposing them.

**How to apply:** Do not move these values into the general settings table or source code. Treat database-file access as equivalent to access to the session-signing secret.