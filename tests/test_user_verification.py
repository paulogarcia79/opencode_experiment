import pytest
from sqlmodel import Session, select
from app.models.user import User
from app.models.user_oauth_provider import UserOAuthProvider


class TestUserVerificationFields:
    """Test that User model has verification-related fields."""

    def test_user_has_is_verified_field_defaults_false(self, session: Session):
        """New users should have is_verified=False by default."""
        user = User(
            email="unverified@example.com",
            hashed_password="some-hash",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.is_verified is False

    def test_user_has_verification_token_hash_nullable(self, session: Session):
        """verification_token_hash should be nullable."""
        user = User(
            email="test@example.com",
            hashed_password="some-hash",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.verification_token_hash is None

    def test_user_has_verification_token_expires_at_nullable(self, session: Session):
        """verification_token_expires_at should be nullable."""
        user = User(
            email="test@example.com",
            hashed_password="some-hash",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.verification_token_expires_at is None

    def test_seed_admin_is_verified(self, session: Session):
        """The seeded admin user should be verified (grandfathered in)."""
        from app.config import settings
        admin = session.exec(select(User).where(User.email == settings.ADMIN_EMAIL)).first()
        assert admin is not None
        assert admin.is_verified is True


class TestUserOAuthProviderModel:
    """Test the UserOAuthProvider model."""

    def test_create_oauth_provider(self, session: Session):
        """Can create a UserOAuthProvider linked to a user."""
        user = session.exec(select(User)).first()
        provider = UserOAuthProvider(
            user_id=user.id,
            provider="google",
            provider_user_id="google-12345",
        )
        session.add(provider)
        session.commit()
        session.refresh(provider)
        assert provider.id is not None
        assert provider.user_id == user.id
        assert provider.provider == "google"
        assert provider.provider_user_id == "google-12345"
        assert provider.created_at is not None

    def test_unique_constraint_provider_user_id(self, session: Session):
        """Cannot create duplicate (provider, provider_user_id) pairs."""
        user = session.exec(select(User)).first()
        provider1 = UserOAuthProvider(
            user_id=user.id,
            provider="google",
            provider_user_id="google-12345",
        )
        session.add(provider1)
        session.commit()

        provider2 = UserOAuthProvider(
            user_id=user.id,
            provider="google",
            provider_user_id="google-12345",
        )
        session.add(provider2)
        with pytest.raises(Exception):
            session.commit()

    def test_same_user_multiple_providers(self, session: Session):
        """A user can have multiple OAuth providers."""
        user = session.exec(select(User)).first()
        google = UserOAuthProvider(user_id=user.id, provider="google", provider_user_id="g-1")
        github = UserOAuthProvider(user_id=user.id, provider="github", provider_user_id="gh-1")
        session.add(google)
        session.add(github)
        session.commit()

        providers = session.exec(
            select(UserOAuthProvider).where(UserOAuthProvider.user_id == user.id)
        ).all()
        assert len(providers) == 2

    def test_different_users_same_provider(self, session: Session):
        """Different users can have the same provider_user_id (different Google accounts)."""
        user1 = User(email="user1@example.com", hashed_password="hash1", is_verified=True)
        user2 = User(email="user2@example.com", hashed_password="hash2", is_verified=True)
        session.add(user1)
        session.add(user2)
        session.commit()

        p1 = UserOAuthProvider(user_id=user1.id, provider="google", provider_user_id="g-1")
        p2 = UserOAuthProvider(user_id=user2.id, provider="google", provider_user_id="g-2")
        session.add(p1)
        session.add(p2)
        session.commit()

        providers = session.exec(select(UserOAuthProvider)).all()
        assert len(providers) == 2
