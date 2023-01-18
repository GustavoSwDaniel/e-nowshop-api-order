import abc
from sqlalchemy.orm import Session


class IRepository(metaclass=abc.ABCMeta):
    def __init__(self, session_factory: Session) -> None:
        self.session_factory = session_factory
