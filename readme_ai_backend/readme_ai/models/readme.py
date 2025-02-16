from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from readme_ai.models.base import Base


class Readme(Base):
    __tablename__ = "readmes"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    repository_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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

    readme = relationship("Readme", back_populates="versions")
    chat_message = relationship("ChatMessage", back_populates="version", uselist=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    readme_id = Column(Integer, ForeignKey("readmes.id"), nullable=False)
    readme_version_id = Column(Integer, ForeignKey("readme_versions.id"), nullable=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    readme = relationship("Readme", back_populates="chat_messages")
    version = relationship("ReadmeVersion", back_populates="chat_message")
