import discord
import os
import asyncio
import random 
import requests
import random
import json
import openai

from discord.ext import commands, tasks
from datetime import datetime, timedelta
from dotenv import load_dotenv

from frases import frases
from opinion import opinion
from cards import cards
from responses import responses

# Load the .env file that contains the bot token
load_dotenv()
TOKEN = os.getenv('TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Functions
def get_random_morning_time():
    random_hour = random.randint(13, 13)  # Random hour between 8 AM and 11 AM
    random_minute = random.randint(7, 8)  # Random minute between 0 and 59
    res =  datetime.now().replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
    print(f"Next message scheduled for: {res}")
    return res

target_time = None

@bot.event
async def on_ready():
    global target_time
    print(f'Logged in as {bot.user.name}')
    
    # Set initial target time when bot is ready
    target_time = get_random_morning_time()
    print("Target time is")
    it = 0 
    while (target_time < datetime.now() and it<10):  # If the random time has already passed, set it for tomorrow
        target_time = get_random_morning_time()
        it = it + 1
    if it == 10:
        target_time += timedelta(days=1)
    print(f"Next message scheduled for: {target_time}")

    # Start the repeating task
    check_and_send_message.start()

@tasks.loop(minutes=1)
async def check_and_send_message():
    global target_time
    now = datetime.now()

    # Check if it's time to send the message
    if target_time <= now < target_time + timedelta(minutes=5):
        channel = bot.get_channel(1304347189379858452)  # Replace with your channel ID
        await channel.send("Good morning! This is your daily message.")

        # Set the next target time to a random time in the morning tomorrow
        target_time = get_random_morning_time() + timedelta(days=1)
        print(f"Next message scheduled for: {target_time}")

# Set the confirmation message when the bot is ready

@bot.command(name="helpp")
async def help(ctx):
    response = "Nobody can help you"
    await ctx.send(response)

@bot.command(name="ask")
async def ask(ctx, *, question=None):
    if question is None:
        res = "No me hiciste ninguna pregunta"
    else:
        response_index = random.randint(0,4)
        res = responses[response_index]
    await ctx.send(res)

# Example command

@bot.command(aliases=["cual"])
async def quien(ctx, *, choices: str):
    options = choices.split(" o ")
    last = ['', '!', '!!']
    last_index = random.randint(0,2)
    if len(options) == 2:
        winner = random.choice(options)
        await ctx.send(f"{winner.strip()}{last[last_index]}")
    else:
        await ctx.send("Mal formulado")


@bot.command(name="cody")
async def cody(ctx):
    after_cody_array = [": ", "... ", "! ", "!! ", " :) "]
    after_cody_index = random.randint(0,4)
    response = "Cody" + after_cody_array[after_cody_index]
    len_frases = len(frases)
    index = random.randint(0, len_frases-1)
    response = response + frases[index]
    await ctx.send(response)

@bot.command(name="horoscope")
async def horoscope(ctx, sign: str):
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {
    "sign": sign,
    "day": "TODAY"
    }
    headers = {
    "accept": "application/json"
    }
    response = requests.get(url, headers=headers, params=params)
    res = response
    await ctx.send(res.json()['data']['horoscope_data'])

@bot.command(name="card")
async def card(ctx):
    len_cards = len(cards)
    index = random.randint(0, len_cards-1)
    response = cards[index]
    await ctx.send(response)
# Background task to send a message at 10:00 AM every day
@tasks.loop(hours=24)
async def send_daily_hello():
    now = datetime.now()
    target_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # If it's already past 10:00 AM today, set target to 10:00 AM tomorrow
    if now >= target_time:
        target_time += timedelta(days=1)

    # Calculate how many seconds until 10:00 AM
    wait_time = (target_time - now).total_seconds()
    await asyncio.sleep(wait_time)  # Wait until 10:00 AM
    
    # Replace 'your-channel-id' with the ID of the channel where you want the message to be sent
    channel = bot.get_channel(1304347189379858452)  # Replace with your channel ID
    await channel.send("Hello! It's 10:00 AM!")

# Background task to send a message every minute
@tasks.loop(minutes=5)
async def send_minutely_hi():
    channel = bot.get_channel(1305942778265468949)
    if channel is not None:
        await channel.send("Hi! This message is sent every 5 minutes.")
    else:
        print("Channel not found. Please check the channel ID.")

# Error handling for the send_minutely_hi task
@send_minutely_hi.before_loop
async def before_send_minutely_hi():
    await bot.wait_until_ready()  # Wait until the bot is fully ready


@bot.command(name="random")
async def random_mention(ctx):
    # Fetch the list of members in the server
    members = [member for member in ctx.guild.members if not member.bot]  # Exclude bots
    if members:
        random_member = random.choice(members)  # Select a random member
        await ctx.send(f"{random_member.mention}, te voy a follar en general")


@bot.command()
async def que(ctx, *, message: str):
    # Check if the message starts with "do you think" (case-insensitive)
    if message.lower().startswith("pensas") or message.lower().startswith("opinas"):
        len_opinion = len(opinion)
        index = random.randint(0, len_opinion-1)
        res = opinion[index]
        await ctx.send(res)


ACCESS_TOKEN = "CXyFeSBw2lAdG41xkuU3LS6a_nwyxwwCz2dCkUohw-rw0C49x2HqP__6_4is5RPx"
BASE_URL = "https://api.genius.com/songs/"
MAX_SONG = 2471960  # You can adjust this value

def get_random_song():
    while True:
        # Generate a random song ID
        song_id = random.randint(1, MAX_SONG)
        url = f"{BASE_URL}{song_id}?access_token={ACCESS_TOKEN}"
        
        # Make the API call
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse and return the song data
            data = response.json()
            song = data['response']['song']
            print(song)
            return {
                "title": song['title'],
                "artist": song['primary_artist']['name'],
                "image": song['header_image_thumbnail_url'],
                "url":song['url']
            }
            

        elif response.status_code == 404:
            # Song not found, retry
            continue
        else:
            # Handle other errors
            raise Exception(f"Error: {response.status_code}, {response.text}")

# Fetch a random song
@bot.command(name="song")
async def song(ctx):
    try:
        random_song = get_random_song()
        print(json.dumps(random_song, indent=4))  # Pretty-print the result
        await ctx.send(f"Tu canción es: {random_song['title']} de {random_song['artist']} ")
        await ctx.send(f"{random_song['image']}")
        await ctx.send(f"Ver cancion:")
        await ctx.send(f"{random_song['url']}")
    except Exception as e:
        print(e)
# Run the bot
bot.run(TOKEN)
