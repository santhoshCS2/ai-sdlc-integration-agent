from sqlalchemy import text
from app.core.database import Base, engine
from app.models.user import User

def reset_database():
    print("Creating schema 'integrationagent' if not exists...")
    with engine.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS integrationagent"))
        connection.commit()

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done!")

if __name__ == "__main__":
    reset_database()
