from datetime import datetime

from app.models.oauth_state import OAuthState


class OAuthStateRepository:

    @staticmethod
    def create(
        db,
        state: str,
        user_id: str,
        expires_at: datetime
    ) -> OAuthState:
        oauth_state = OAuthState(
            state=state,
            user_id=user_id,
            expires_at=expires_at
        )

        db.add(oauth_state)
        db.commit()
        db.refresh(oauth_state)

        return oauth_state

    @staticmethod
    def get_by_state(
        db,
        state: str
    ) -> OAuthState | None:
        return (
            db.query(OAuthState)
            .filter(OAuthState.state == state)
            .first()
        )

    @staticmethod
    def mark_used(
        db,
        oauth_state: OAuthState,
        used_at: datetime
    ) -> OAuthState:
        oauth_state.used_at = used_at
        db.commit()
        db.refresh(oauth_state)

        return oauth_state

    @staticmethod
    def delete_expired(
        db,
        now: datetime
    ) -> None:
        (
            db.query(OAuthState)
            .filter(OAuthState.expires_at < now)
            .delete()
        )
        db.commit()