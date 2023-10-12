from __future__ import annotations

import asyncio
import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Chat(Base):
    __tablename__ = "chat"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)

class Tournament(Base):
    __tablename__ = "tournament"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    finish: Mapped[bool] = mapped_column(default=False)

class ChatTournament(Base):
    __tablename__ = "chat_tournament"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournament.id"))

    chat: Mapped[Chat] = relationship()
    tournament: Mapped[Tournament] = relationship()

class Team(Base):
    __tablename__ = "team"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournament.id"))

    tournament: Mapped[Tournament] = relationship()


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournament.id"))

    tournament: Mapped[Tournament] = relationship()


class Score(Base):
    __tablename__ = "score"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"))
    goals: Mapped[int]


    team: Mapped[Team] = relationship()
    game: Mapped[Game] = relationship()

