---
name: Flask PWA service worker scope
description: Root-scope service workers in Flask must be exposed outside the static directory.
---

Serve a PWA service worker from the origin root when it needs to control the whole Flask app; registering a script under `/static/` cannot claim `/` without an explicit Service-Worker-Allowed header.

**Why:** Browsers enforce the service worker script directory as the default maximum scope, so a static-directory worker silently fails to register for the app root.

**How to apply:** Keep the source in `static/` if desired, but add a root route such as `/service-worker.js` and register that URL with scope `/`.