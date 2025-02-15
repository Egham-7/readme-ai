from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Readme(Base):
    __tablename__ = "readmes"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    repository_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    versions = relationship(
        "ReadmeVersion", back_populates="readme", cascade="all, delete-orphan"
    )
    chat_messages = relationship(
        "ChatMessage", back_populates="readme", cascade="all, delete-orphan"
    )


class ReadmeVersion(Base):
    __tablename__ = "readme_versions"

    id = Column(Integer, primary_key=True)
    readme_id = Column(Integer, ForeignKey("readmes.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    readme = relationship("Readme", back_populates="versions")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    readme_id = Column(Integer, ForeignKey("readmes.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    readme = relationship("Readme", back_populates="chat_messages")
