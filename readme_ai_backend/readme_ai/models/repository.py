from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from readme_ai.models.base import Base
from pgvector.sqlalchemy import Vector  # type: ignore


class Repository(Base):
    __tablename__ = "repositories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    url: Mapped[str] = mapped_column(String, unique=True, index=True)
    # Foreign key relationship with User
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.clerk_id"), index=True
    )
    user = relationship("User", back_populates="repositories")
    # Relationship with FileContent
    file_contents = relationship("FileContent", back_populates="repository")
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class FileContent(Base):
    __tablename__ = "file_contents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    # Foreign key relationship with Repository
    repository_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repositories.id"), index=True
    )
    repository = relationship("Repository", back_populates="file_contents")
    content_embedding: Mapped[Vector] = mapped_column(Vector[1536])
    path: Mapped[str] = mapped_column(String, nullable=False)
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
