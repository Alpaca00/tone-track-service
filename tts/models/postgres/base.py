import uuid

from cryptography.fernet import Fernet
from pydantic import BaseModel, constr
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy import create_engine, Column, String, TIMESTAMP, func
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

from tts.extensions import config_tts, configurations
from tts.helpers.constants import EnvironmentVariables

Base = declarative_base()


class PostgresDatabaseConfig:
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


DATABASE_URL = PostgresDatabaseConfig.get_database_url()

engine = create_engine(DATABASE_URL, echo=True)

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)


class Channel(Base):
    """The channel model for SQLAlchemy."""

    __tablename__ = "channels"  # noqa

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    team_id = Column(BYTEA, nullable=False, unique=True)
    team_domain = Column(String(55), nullable=False)
    channel_id = Column(String(55), nullable=False, unique=True)
    channel_name = Column(String(55), nullable=False)
    sentiment_message = Column(String(100), nullable=False)
    registered_on = Column(TIMESTAMP, server_default=func.now())


class ChannelCreate(BaseModel):
    """The channel model for Pydantic."""

    team_id: constr(max_length=255, min_length=1)
    team_domain: constr(max_length=55, min_length=1)
    channel_id: constr(max_length=55, min_length=1)
    channel_name: constr(max_length=55, min_length=1)
    sentiment_message: constr(max_length=100, min_length=1)


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
    """The database manager."""

    @staticmethod
    def get_secret_key() -> bytes:
        """Return the secret key."""
        environment = config_tts.project.environment
        secret_key = configurations[environment].SECRET_KEY
        return secret_key.encode()

    @staticmethod
    def encrypt(data: str) -> bytes:
        """Encrypt data."""
        fernet = Fernet(DatabaseManager.get_secret_key())
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data

    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """Decrypt data."""
        fernet = Fernet(DatabaseManager.get_secret_key())
        try:
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception:  # noqa
            return encrypted_data

    @staticmethod
    def add_channel_sentiment_message(
        team_id: str,
        team_domain: str,
        channel_id: str,
        channel_name: str,
        sentiment_message: str,
    ):
        """Add a channel to the database."""
        with SessionManager() as session:
            encrypted_team_id = DatabaseManager.encrypt(team_id)

            new_channel = Channel(
                team_id=encrypted_team_id,
                team_domain=team_domain,
                channel_id=channel_id,
                channel_name=channel_name,
                sentiment_message=sentiment_message,
            )
            session.add(new_channel)
            return new_channel

    @staticmethod
    def read_channel_sentiment_message(channel_id: str):
        """Retrieve a channel by ID."""
        with SessionManager() as session:
            channel = (
                session.query(Channel)
                .filter(Channel.channel_id == channel_id)
                .first()
            )
            if channel:
                return channel.sentiment_message
            return None

    @staticmethod
    def update_channel_sentiment_message(channel_id: str, sentiment_message: str):
        """Update a channel sentiment message."""
        with SessionManager() as session:
            channel = session.query(Channel).filter(Channel.channel_id == channel_id).first()
            channel.sentiment_message = sentiment_message
            return channel


def initialize_database():
    """Initialize the database."""
    Base.metadata.create_all(engine)
