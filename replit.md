# PDF to Anything on Replit

## Run

- The app runs with the `Start application` workflow.
- The workflow command is `python app.py` and serves on port 5000.
- Python dependencies are installed from `requirements.txt`.

## Environment

- Security credentials use the SQLite-backed mode: the session secret is generated once and persisted in the `security_credentials` table, and the admin password is stored only as a salted hash there.
- `SECRET_KEY` and `ADMIN_PASSWORD` environment overrides are intentionally not used by this mode.
- The app uses the Replit-provided database URL when available, otherwise it falls back to SQLite.

## Notes

- PDF image conversion uses the `poppler-utils` system dependency.
- The app creates its upload, output, and temporary storage directories at startup.
- The app is an installable PWA when served over HTTPS (or localhost): the manifest and icons live under `static/`, the service worker is exposed at `/service-worker.js` so it can control the `/` scope, and offline navigation falls back to `static/offline.html`.
- PWA icon artwork is sourced from `static/icons/icon-source.svg` and `static/icons/maskable-icon-source.svg`; regenerate the PNG variants if the branding changes.