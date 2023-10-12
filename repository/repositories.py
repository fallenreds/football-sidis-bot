from repository.base import BaseRepository
from db.models import *


class TournamentRepository(BaseRepository):
    model = Tournament

    async def create(self, **kwargs) -> Tournament:
        return await super().create(**kwargs)


class GameRepository(BaseRepository):
    model = Game


class ChatTournamentRepository(BaseRepository):
    model = ChatTournament

    async def create(self, chat_id: int, tournament_id: int, **kwargs) -> ChatTournament:
        kwargs['chat_id'] = chat_id
        kwargs['tournament_id'] = tournament_id
        return await super().create(**kwargs)

    async def last(self, chat_id) -> ChatTournament | None:
        tournaments = await self.session.execute(
            select(self.model).filter(self.model.chat_id == chat_id).order_by(self.model.id.desc()).limit(1)
        )
        return tournaments.scalar_one_or_none()


class TeamRepository(BaseRepository):
    model = Team

    async def create(self, tournament_id: int, name: str, **kwargs) -> Team:
        kwargs['name'] = name
        kwargs['tournament_id'] = tournament_id
        return await super().create(**kwargs)


class ScoreRepository(BaseRepository):
    model = Score


class ChatStatisticMessageRepository(BaseRepository):
    model = ChatStatisticMessage

class ChatRepository(BaseRepository):
    model = Chat