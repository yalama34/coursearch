from src.dependencies.db import SessionDep


class BaseRepository:
    def __init__(
            self,
            session: SessionDep,
    ):
        self.session = session
