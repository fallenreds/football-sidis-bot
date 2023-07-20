from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterTeamsStorage(StatesGroup):
    first = State()
    second = State()
    third = State()


class GameStorage(StatesGroup):
    first_team = State()
    second_team = State()
    results = State()

    # first_result = State()
    # second_result = State()

class EditGameStorage(StatesGroup):
    first_team = State()
    second_team = State()
    results = State()