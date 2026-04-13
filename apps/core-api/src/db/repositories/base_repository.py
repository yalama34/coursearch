from src.db.database import SessionDep


class BaseRepository:
    def __init__(
            self,
            session: SessionDep,
    ):
        self.session = session
