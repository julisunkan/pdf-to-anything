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