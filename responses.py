from random import choice, randint
import requests
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('API_KEY')
MEME_KEY = os.getenv('MEME_KEY')

# Base URL for the API
BASE_URL = 'https://v6.exchangerate-api.com/v6/'


def get_meme(query):
    MEME_KEY = os.getenv('MEME_KEY')
    response = requests.get(f'https://api.giphy.com/v1/gifs/search?api_key={MEME_KEY}&q={query}&limit=1')
    data = response.json()
    if data['data']:
        gif_url = data['data'][0]['images']['original']['url']
        return gif_url
    else:
        return "No results found"

def get_random_meme():
    MEME_KEY = os.getenv('MEME_KEY')
    response = requests.get(f'https://api.giphy.com/v1/gifs/random?api_key={MEME_KEY}&tag=&rating=g')
    data = response.json()
    if data.get('data'):
        gif_url = data['data']['images']['original']['url']
        return gif_url
    else:
        return "No results found"

# Example usage:
#print(get_meme(input('search:')))


def get_exchange_rates(base_currency,target_currency):
    url = f'{BASE_URL}{API_KEY}{base_currency}'
    response = requests.get(url)
    data = response.json()
    return "1 " + base_currency + " --> " + str(data['conversion_rates'][target_currency]) + " " + target_currency


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " - " + json_data[0]['a']
    return quote


def get_random_event():
    response = requests.get("https://today.zenquotes.io/api/")
    json_data = json.loads(response.text)
    events = json_data['data']['Events']

    if events:
        event = random.choice(events)
        event_description = f'On this day in {event.get('text', 'No description available')}'
        return event_description[:19] + '' + event_description[26:]
    else:
        return "No events found for today."




def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()
    print(lowered)
    if lowered == '':
        return 'Well, you\'re awfully silent...'
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'how are you' in lowered:
        return 'Good, thanks!'
    elif 'bye' in lowered:
        return 'Leaving so soon, Bye!'
    elif 'roll dice' in lowered:
        return f'You rolled: {randint(1,6)}'
    elif 'inspire me' in lowered:
        return get_quote()
    elif 'on this day' in lowered:
        return get_random_event()
    elif 'what is the currency exchange of' in lowered:
        base_currency = lowered[33:36].upper()
        target_currency = lowered[40:43].upper()
        return get_exchange_rates(base_currency,target_currency)
    else:
        return choice(['I do not understand...',
                       'What do you mean?'
                       'Do you mind rephrasing?'])