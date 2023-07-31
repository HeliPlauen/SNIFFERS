import datetime
import time
import pyautogui
import subprocess
import os


# Create the counting game costs function
def coin_counter(start_date_time, price, rest_money):
    game_time = 1
    rest_money -= price
    print(f"The rest money is: {rest_money}")

    # Turn integer into time
    game_time_delta = datetime.timedelta(minutes=game_time)
    print(game_time_delta)
    end_game_time = start_date_time + game_time_delta
    print(f"The end game time is: {end_game_time}")

    # Determining the remaining playing time of users
    remain_game_time = rest_money // price

    # Prepare answer dictionary for returning
    answer_data = {"rest_money": rest_money, "game_time": game_time, "remain_game_time": remain_game_time}
    print(f"Answer data: {answer_data}")
    return answer_data

