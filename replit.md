# PDF to Anything on Replit

## Run

- The app runs with the `Start application` workflow.
- The workflow command is `python app.py` and serves on port 5000.
- Python dependencies are installed from `requirements.txt`.

## Environment

- `SESSION_SECRET` is used as the Flask secret key when `SECRET_KEY` is not set.
- `ADMIN_PASSWORD` can be set as a Replit Secret to protect the admin panel.
- The app uses the Replit-provided database URL when available, otherwise it falls back to SQLite.

## Notes

- PDF image conversion uses the `poppler-utils` system dependency.
- The app creates its upload, output, and temporary storage directories at startup.