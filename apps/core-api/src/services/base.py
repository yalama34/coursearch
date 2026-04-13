from src.dependencies.db import SessionDep


class BaseService:
    def __init__(
            self,
            session: SessionDep,
    ):
        self.session = session
