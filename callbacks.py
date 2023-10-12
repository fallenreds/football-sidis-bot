from aiogram.utils.callback_data import CallbackData

team_callback = CallbackData('team', 'team_id')
team_goal_callback = CallbackData('team_goal', 'result')
team_color = CallbackData('set_team_color', 'color')

plus_team_score = CallbackData("plus_team_score", "team_key")
minus_team_score = CallbackData("minus_team_score", "team_key")

edit_game_callback = CallbackData('edit_game', "row_number")
