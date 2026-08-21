---
name: Anonymous format UI
description: The homepage is anonymous while the formats API is authenticated.
---

The anonymous homepage should use server-rendered format data for its format picker rather than calling the API endpoint that requires an API key.

**Why:** A browser request without the API key receives an authorization error, leaving the picker empty even though formats are available.

**How to apply:** Keep the authenticated API for programmatic clients, and pass available formats into the homepage template for the public upload flow.