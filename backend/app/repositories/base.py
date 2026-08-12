from typing import Generic, TypeVar
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]):
        self.db = db
        self.model = model

    def get(self, entity_id: int):
        return self.db.get(self.model, entity_id)

    def delete(self, entity):
        self.db.delete(entity)
        return entity

    def save(self, entity):
        self.db.add(entity)
        self.db.flush()
        return entity
