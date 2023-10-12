from repository.repositories import *
from settings import db_url
from typing import List, Tuple


class TournamentWorker:
    def __init__(self):
        self.tournament_repo = TournamentRepository(db_url)
        self.chat_tournament_repo = ChatTournamentRepository(db_url)
        self.team_repo = TeamRepository(db_url)
        self.game_repo = GameRepository(db_url)
        self.score_repo = ScoreRepository(db_url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.tournament_repo.close()
        await self.chat_tournament_repo.close()
        await self.team_repo.close()
        await self.game_repo.close()
        await self.score_repo.close()

    async def start(self, chat_id: int, teams: list[str]) -> Tournament:
        """
        Start Tournament and create teams for tournament
        :param chat_id:
        :param teams:
        :return:
        """
        tournament = await self.tournament_repo.create()
        for team in teams:
            await self.team_repo.create(tournament.id, team)
        await self.chat_tournament_repo.create(chat_id, tournament.id)
        return tournament

    async def get_chat_tournaments(self, chat_id) -> list[Tournament]:
        return await self.chat_tournament_repo.list(chat_id=chat_id)

    async def get_last_tournament(self, chat_id) -> Tournament | None:
        last_chat_tournament = await self.chat_tournament_repo.last(chat_id)
        return await self.tournament_repo.get(
            id=last_chat_tournament.tournament_id
        )

    async def is_registered_tournament(self, chat_id) -> bool:
        return bool(await self.get_chat_tournaments(chat_id))

    async def get_teams(self, tournament_id: int):
        return [team for team in await self.team_repo.list(tournament_id=tournament_id)]

    async def get_team(self, team_id) -> Team:
        return await self.team_repo.get(id=team_id)

    async def add_game(self, tournament_id, result: List[Tuple[int, int]]):
        """
            Expects a list of tuples where each tuple represents information about a team and its score.

            :param result: List of tuples in the format [(team_id, score), ...]
            :param tournament_id: id of current tournament

            Example:
                your_function([(1, 23), (2, 12)])

        """

        game = await self.game_repo.create(tournament_id=tournament_id)
        for team_score in result:
            await self.score_repo.create(
                team_id=team_score[0],
                game_id=game.id,
                goals=team_score[1]
            )

    async def get_game_results(self, game_id):
        game = await self.game_repo.get(id=game_id)
        scores = [score for score in await self.score_repo.list(game_id=game_id)]
        teams = await self.get_teams(game.tournament_id)

        data = []

        async def get_team_score(team_id):
            for score in scores:
                if score.team_id == team_id:
                    return score.goals
            return 'H'

        for team in teams:
            score = await get_team_score(team.id)
            data.append(score)
        return data

    async def get_tournament_data(self, tournament_id) -> list[list]:
        games = await self.game_repo.list(tournament_id=tournament_id)
        data = []
        for game in games:
            data.append(
                await self.get_game_results(game.id)
            )

        return data

    async def get_result(self, tournament_id):
        data = await self.get_tournament_data(tournament_id)
        return [self.determine_results(result) for result in data]

    async def edit_game(self, game_id: int, result: List[Tuple[int, int]]):
        """
            Expects a list of tuples where each tuple represents information about a team and its score.

            :param result: List of tuples in the format [(team_id, score), ...]
            :param tournament_id: id of current tournament

            Example:
                your_function([(1, 23), (2, 12)])

        """
        await self.score_repo.delete(game_id=game_id)
        for team_score in result:
            await self.score_repo.create(
                team_id=team_score[0],
                game_id=game_id,
                goals=team_score[1]
            )

    @staticmethod
    def determine_results(data: list):
        results = []

        if data[0] == "H":
            results.append('Не учавствовал')

            if int(data[1]) > int(data[2]):
                results.append('Победил')
                results.append('Проиграл')
            elif int(data[1]) < int(data[2]):
                results.append('Проиграл')
                results.append('Победил')
            elif int(data[1]) == int(data[2]):
                results.append('Ничья')
                results.append('Ничья')

        elif data[1] == "H":
            if int(data[0]) > int(data[2]):
                results.append('Победил')
                results.append('Не учавствовал')
                results.append('Проиграл')
            elif int(data[0]) < int(data[2]):
                results.append('Проиграл')
                results.append('Не учавствовал')
                results.append('Победил')
            elif int(data[0]) == int(data[2]):
                results.append('Ничья')
                results.append('Не учавствовал')
                results.append('Ничья')
        elif data[2] == "H":
            if int(data[0]) > int(data[1]):
                results.append('Победил')
                results.append('Проиграл')
            elif int(data[0]) < int(data[1]):
                results.append('Проиграл')
                results.append('Победил')
            elif int(data[0]) == int(data[1]):
                results.append('Ничья')
                results.append('Ничья')
            results.append('Не учавствовал')
        return results


class StatisticWorker:
    def __init__(self):
        self.statistic = ChatStatisticMessageRepository(db_url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.statistic.close()

    async def get_chat_statistic_message(self, chat_id: int)->ChatStatisticMessage:
        return await self.statistic.get(chat_id=chat_id)

    async def update_statistic_message(self, chat_id: int, message_id: int)->ChatStatisticMessage:
        statistic_message = await self.get_chat_statistic_message(chat_id)

        if not statistic_message:
            return await self.statistic.create(chat_id=chat_id, message_id=message_id)

        return await self.statistic.update(update_data={"message_id": message_id}, id=statistic_message.id)

