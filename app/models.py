import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import BaseModel


class Anime(BaseModel):
    __tablename__ = "animes"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    episodes: Mapped[list[Episode]] = relationship(
        back_populates="episodes.anime_id", cascade="all, delete-orphan"
    )


class Episode(BaseModel):
    __tablename__ = "episodes"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    anime_id: Mapped[int] = mapped_column(
        ForeignKey(column="animes.id", ondelete="CASCADE"), index=True
    )

    anime: Mapped[Anime] = relationship(back_populates="episodes")
