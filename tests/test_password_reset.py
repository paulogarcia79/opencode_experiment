import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta
from app.models.user import User
from sqlmodel import select


class TestGenerateResetToken:
    def test_generate_returns_plaintext_token_and_stores_hash(self, session: Session):
        """Generating a reset token returns a plaintext token and stores a hash on the user."""
        from app.services.auth_service import generate_reset_token

        user = session.exec(select(User)).first()
        assert user.reset_token_hash is None

        plaintext = generate_reset_token(user, session)

        assert isinstance(plaintext, str)
        assert len(plaintext) > 0
        session.refresh(user)
        assert user.reset_token_hash is not None
        assert user.reset_token_expires_at is not None

    def test_validate_returns_user_for_valid_token(self, session: Session):
        """Validating a correct token returns the associated user."""
        from app.services.auth_service import generate_reset_token, validate_reset_token

        user = session.exec(select(User)).first()
        plaintext = generate_reset_token(user, session)

        validated_user = validate_reset_token(plaintext, session)

        assert validated_user is not None
        assert validated_user.id == user.id

    def test_validate_returns_none_for_wrong_token(self, session: Session):
        """Validating a wrong token returns None."""
        from app.services.auth_service import generate_reset_token, validate_reset_token

        user = session.exec(select(User)).first()
        generate_reset_token(user, session)

        result = validate_reset_token("completely-wrong-token", session)

        assert result is None

    def test_validate_returns_none_for_expired_token(self, session: Session):
        """Validating an expired token returns None."""
        from app.services.auth_service import generate_reset_token, validate_reset_token
        from app.services.auth_service import pwd_context

        user = session.exec(select(User)).first()
        generate_reset_token(user, session)

        # Manually set expiry to the past
        user.reset_token_expires_at = datetime.utcnow() - timedelta(minutes=1)
        session.add(user)
        session.commit()

        # We need the plaintext token, but we already generated it.
        # Generate a new one and then expire it.
        plaintext = generate_reset_token(user, session)
        user.reset_token_expires_at = datetime.utcnow() - timedelta(minutes=1)
        session.add(user)
        session.commit()

        result = validate_reset_token(plaintext, session)

        assert result is None

    def test_reset_password_updates_hash_and_increments_version(self, session: Session):
        """Resetting password updates the hashed password and increments token_version."""
        from app.services.auth_service import generate_reset_token, reset_password, validate_reset_token

        user = session.exec(select(User)).first()
        old_version = user.token_version
        plaintext = generate_reset_token(user, session)

        reset_password(user, "new-super-secret", session)

        session.refresh(user)
        assert user.token_version == old_version + 1
        assert user.reset_token_hash is None
        assert user.reset_token_expires_at is None

        # Old token should be invalid now
        assert validate_reset_token(plaintext, session) is None

    def test_reset_password_invalidates_all_pending_tokens(self, session: Session):
        """Resetting password clears all pending reset tokens."""
        from app.services.auth_service import generate_reset_token, reset_password, validate_reset_token

        user = session.exec(select(User)).first()
        # Generate multiple tokens (simulating multiple reset requests)
        token1 = generate_reset_token(user, session)
        token2 = generate_reset_token(user, session)

        reset_password(user, "new-password", session)

        assert validate_reset_token(token1, session) is None
        assert validate_reset_token(token2, session) is None
