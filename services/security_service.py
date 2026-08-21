import hashlib
import hmac
import secrets

from werkzeug.security import check_password_hash, generate_password_hash

from models import db, SecurityCredential


class SecurityService:
    """Persist bootstrap security material without exposing it as app settings."""

    SESSION_SECRET_NAME = 'session_secret'
    ADMIN_PASSWORD_NAME = 'admin_password_hash'

    @staticmethod
    def _get(name):
        return SecurityCredential.query.filter_by(name=name).first()

    @staticmethod
    def initialize(app):
        """Load or create a persistent session secret after the database is ready."""
        configured_secret = app.config.get('SECRET_KEY')
        credential = SecurityService._get(SecurityService.SESSION_SECRET_NAME)

        if configured_secret:
            app.config['SECRET_KEY'] = configured_secret
            if not credential:
                credential = SecurityCredential(
                    name=SecurityService.SESSION_SECRET_NAME,
                    value=configured_secret,
                )
                db.session.add(credential)
                db.session.commit()
            return

        if not credential:
            credential = SecurityCredential(
                name=SecurityService.SESSION_SECRET_NAME,
                value=secrets.token_urlsafe(48),
            )
            db.session.add(credential)
            db.session.commit()

        app.config['SECRET_KEY'] = credential.value

    @staticmethod
    def set_admin_password(password):
        """Store only a salted password hash."""
        credential = SecurityService._get(SecurityService.ADMIN_PASSWORD_NAME)
        password_hash = generate_password_hash(password)
        if not credential:
            credential = SecurityCredential(
                name=SecurityService.ADMIN_PASSWORD_NAME,
                value=password_hash,
            )
            db.session.add(credential)
        else:
            credential.value = password_hash
        db.session.commit()

    @staticmethod
    def verify_admin_password(password, configured_password=None):
        """Verify against a legacy environment value or the database hash."""
        if configured_password:
            return hmac.compare_digest(password or '', configured_password)

        credential = SecurityService._get(SecurityService.ADMIN_PASSWORD_NAME)
        return bool(credential and check_password_hash(credential.value, password or ''))

    @staticmethod
    def has_admin_password():
        return SecurityService._get(SecurityService.ADMIN_PASSWORD_NAME) is not None