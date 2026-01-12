from sqlalchemy.orm import Session
from app.models.chat import Conversation, Message
from app.schemas.chat import ConversationCreate, MessageCreate
from datetime import datetime

def create_conversation(db: Session, conversation: ConversationCreate):
    db_conversation = Conversation(**conversation.dict())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation(db: Session, conversation_id: int):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def create_message(db: Session, message: MessageCreate):
    db_message = Message(**message.dict())
    db.add(db_message)
    # Update last_message_at in conversation
    db_conversation = get_conversation(db, message.conversation_id)
    if db_conversation:
        db_conversation.last_message_at = datetime.utcnow()
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, conversation_id: int):
    return db.query(Message).filter(Message.conversation_id == conversation_id).all()
