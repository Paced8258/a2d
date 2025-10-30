from sqlmodel import SQLModel, create_engine, Session
from settings import settings

engine = create_engine(settings.database_url, echo=False)

def get_session():
    with Session(engine) as s:
        yield s

def init_db():
    SQLModel.metadata.create_all(engine)