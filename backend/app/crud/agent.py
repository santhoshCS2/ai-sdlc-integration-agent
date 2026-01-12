from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate

def get_agent(db: Session, agent_id: int):
    return db.query(Agent).filter(Agent.id == agent_id).first()

def get_agents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Agent).offset(skip).limit(limit).all()

def create_agent(db: Session, agent: AgentCreate, owner_id: int):
    db_agent = Agent(**agent.dict(), owner_id=owner_id)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def update_agent(db: Session, agent_id: int, agent: AgentUpdate):
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        return None
    for key, value in agent.dict(exclude_unset=True).items():
        setattr(db_agent, key, value)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def delete_agent(db: Session, agent_id: int):
    db_agent = get_agent(db, agent_id)
    if db_agent:
        db.delete(db_agent)
        db.commit()
    return db_agent
