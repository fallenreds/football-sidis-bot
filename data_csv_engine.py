import csv
from settings import CSV_PATH
from typing import TypedDict
import aiomisc


async def register_teams(data: TypedDict('teams', {'first': 'str', 'second': 'str', 'third': 'str'})):
    await set_headers(list(data.values()))


async def set_headers(headers: list):
    with open(CSV_PATH, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)


async def read_headers() -> list:
    with open(CSV_PATH, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        return list(headers)


async def append_rows(row: list):
    with open(CSV_PATH, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row)


async def edit_csv_row_by_number(file_path, row_number, new_data):
    try:
        with open(file_path, 'r', newline='') as csvfile:
            rows = list(csv.reader(csvfile))
            if row_number < 0 or row_number >= len(rows):
                print(f"Invalid row number. The CSV file has {len(rows)} rows.")
                return

            rows[row_number] = new_data

        with open(file_path, 'w', newline='') as csvfile:
            csv.writer(csvfile).writerows(rows)

        print(f"Row number {row_number} edited successfully.")
    except Exception as e:
        print(f"Error: {e}")

def find_column_number(csv_file, value):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Читаем заголовки колонок

        for i, header in enumerate(headers):
            if header == value:
                return i  # Возвращаем номер колонки (1-based)

    return None




async def add_team_results(data: TypedDict('results', {'first_team': 'str', 'second_team': 'str', 'first_result': 'str',
                                                       'second_result': 'str'})):
    headers = await read_headers()
    values = ['H', 'H', 'H']
    if data['first_team'] in headers:
        values[headers.index(data['first_team'])] = str(data['first_result'])

    if data['second_team'] in headers:
        values[headers.index(data['second_team'])] = str(data['second_result'])

    await append_rows(values)
    return values

async def edit_team_results(data: TypedDict('results', {'first_team': 'str', 'second_team': 'str', 'first_result': 'str',
                                                       'second_result': 'str'}),
                            row_number
                            ):
    headers = await read_headers()
    values = ['H', 'H', 'H']
    if data['first_team'] in headers:
        values[headers.index(data['first_team'])] = str(data['first_result'])

    if data['second_team'] in headers:
        values[headers.index(data['second_team'])] = str(data['second_result'])

    await edit_csv_row_by_number(CSV_PATH, row_number, values)
    return values

def determine_results(data):
    results = []

    if data[0]=='H':
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

    elif data[1] == 'H':
        if int(data[0])>int(data[2]):
            results.append('Победил')
            results.append('Не учавствовал')
            results.append('Проиграл')
        elif int(data[0])<int(data[2]):
            results.append('Проиграл')
            results.append('Не учавствовал')
            results.append('Победил')
        elif int(data[0])==int(data[2]):
            results.append('Ничья')
            results.append('Не учавствовал')
            results.append('Ничья')
    elif data[2] == 'H':
        if int(data[0])>int(data[1]):
            results.append('Победил')
            results.append('Проиграл')
        elif int(data[0])<int(data[1]):
            results.append('Проиграл')
            results.append('Победил')
        elif int(data[0])==int(data[1]):
            results.append('Ничья')
            results.append('Ничья')
        results.append('Не учавствовал')
    return results

async def get_all_rows():
    result = []
    with open(CSV_PATH, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            result.append(row)
    return result
async def calculate_all_games():
    with open(CSV_PATH, 'r') as file:
        reader = csv.reader(file)

        headers = next(reader)
        result = []

        for row in reader:
            result.append(determine_results(row))

        statistic = []

        for i, team in enumerate(headers):
            team_stat = {'wins': 0, 'lose': 0, 'draw': 0, 'points': 0}
            for variant in result:
                if variant[i] == 'Победил':
                    team_stat['wins'] += 1
                    team_stat['points'] += 3
                if variant[i] == 'Проиграл':
                    team_stat['lose'] += 1
                if variant[i] == 'Ничья':
                    team_stat['draw'] += 1
                    team_stat['points'] += 1
            statistic.append(team_stat)
        return statistic

