import uuid

from pydantic import BaseModel, constr
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import create_engine, Column, String, TIMESTAMP, func
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

from tts.helpers.constants import EnvironmentVariables

Base = declarative_base()


class DatabaseConfig:
    """The database configuration."""

    user = EnvironmentVariables.POSTGRES_USER
    password = EnvironmentVariables.POSTGRES_PASSWORD
    db = EnvironmentVariables.POSTGRES_DB
    host = EnvironmentVariables.POSTGRES_HOST

    @classmethod
    def get_database_url(cls):
        """Return the database full URL."""
        return (
            f"postgresql+psycopg2://{cls.user}:{cls.password}@{cls.host}/{cls.db}"
        )


DATABASE_URL = DatabaseConfig.get_database_url()

engine = create_engine(DATABASE_URL, echo=True)

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)


class Workspace(Base):
    """The workspace model."""

    __tablename__ = "workspaces"  # noqa

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(100), nullable=False, unique=None)
    email = Column(String(100), nullable=False, unique=True)
    sentiment_message = Column(String(100), nullable=False)
    registered_on = Column(TIMESTAMP, server_default=func.now())


class WorkspaceCreate(BaseModel):
    """The workspace model for Pydantic."""

    name: constr(max_length=100)
    email: str
    sentiment_message: constr(max_length=100)


class SessionManager:
    """The session manager."""

    def __init__(self):
        self.session = Session()

    def __enter__(self):
        """Return the session object when entering the context manager."""
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        """Commit the session if no exceptions occurred, otherwise rollback."""
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            self.session.close()


class DatabaseManager:
    @staticmethod
    def add_workspace(name: str, email: str, sentiment_message: str):
        """Add a workspace to the database."""
        with SessionManager() as session:
            new_workspace = Workspace(
                name=name, email=email, sentiment_message=sentiment_message
            )
            session.add(new_workspace)
            return new_workspace

    @staticmethod
    def get_workspace_by_email(email: str):
        """Retrieve a workspace by ID."""
        with SessionManager() as session:
            return session.query(Workspace).get(email)

    @staticmethod
    def list_workspaces():
        """List all workspaces."""
        with SessionManager() as session:
            return session.query(Workspace).all()

    @staticmethod
    def update_workspace_by_email(email: str, name: str, sentiment_message: str):
        """Update a workspace by email."""
        with SessionManager() as session:
            workspace = session.query(Workspace).get(email)
            workspace.name = name
            workspace.sentiment_message = sentiment_message
            session.commit()
            return workspace


def initialize_database():
    """Initialize the database."""
    Base.metadata.create_all(engine)
