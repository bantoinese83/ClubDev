# message_service.py
from uuid import UUID
from sqlmodel import Session
from ..db.models import DirectMessage
from ..db.schemas import DirectMessageCreate, DirectMessageUpdate
from ..core.exceptions import ItemNotFoundError, DatabaseError

class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_direct_message(self, message_in: DirectMessageCreate) -> DirectMessage:
        if not message_in.sender_id:
            raise ValueError("sender_id must be provided")
        try:
            message = DirectMessage(**message_in.model_dump())
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        except Exception as e:
            raise DatabaseError(f"Error creating direct message: {e}")

    def get_direct_message(self, message_id: UUID) -> DirectMessage:
        message = self.db.query(DirectMessage).filter(DirectMessage.id == message_id).first()
        if not message:
            raise ItemNotFoundError(f"Direct message with ID {message_id} not found")
        return message

    def update_direct_message(self, message_id: UUID, message_in: DirectMessageUpdate) -> DirectMessage:
        message = self.get_direct_message(message_id)
        for key, value in message_in.model_dump(exclude_unset=True).items():
            setattr(message, key, value)
        self.db.commit()
        self.db.refresh(message)
        return message

    def delete_direct_message(self, message_id: UUID):
        message = self.get_direct_message(message_id)
        self.db.delete(message)
        self.db.commit()