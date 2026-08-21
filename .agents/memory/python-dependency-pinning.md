---
name: Python dependency pinning
description: Dependency-file hygiene for reliable Replit Python installs
---

Keep requirements files deduplicated and use one compatible version declaration per package.

**Why:** Replit's package firewall resolver rejects a requirements file that requests multiple versions of the same package, even when the application itself would only need one version.

**How to apply:** Before installing Python dependencies, remove duplicate entries and reconcile pinned versions; prefer a single tested pin for each direct dependency.