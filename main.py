import os
import discord
from discord import Message
from responses import get_response, get_quote,get_exchange_rates, get_random_event, get_meme, get_random_meme
from discord.ext import commands
from random import randint
from hangGame import HangmanGame
import openai
import youtube_dl
import asyncio

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('API_KEY')
MEME_KEY = os.getenv('MEME_KEY')

command_prefix = '!'
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
# Create bot instance with command prefix '!'
bot = commands.Bot(command_prefix=command_prefix, intents=intents)
games = {}


async def send_message(message: Message,user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    is_private = user_message[0] == '?'

    if is_private:
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        embed = discord.Embed(description=response, color=0x00ff00)
        await message.author.send(embed=embed) if is_private else await message.channel.send(embed=embed)
    except Exception as e:
        print(e)


async def get_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content'].strip()

# Path to FFmpeg executable
FFMPEG_EXECUTABLE_PATH = 'C:\ffmpeg'  # Update this to the actual path
# Create a bot instance with command prefix

# Configure youtube_dl options
ytdl_format_options = {
   'format': 'bestaudio/best',
   'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
   'restrictfilenames': True,
   'noplaylist': True,
   'nocheckcertificate': True,
   'ignoreerrors': False,
   'logtostderr': False,
   'quiet': True,
   'no_warnings': True,
   'default_search': 'auto',
   'source_address': '0.0.0.0'  # Bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
   'executable': FFMPEG_EXECUTABLE_PATH,
   'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
class YTDLSource(discord.PCMVolumeTransformer):
   def __init__(self, source, *, data, volume=0.5):
       super().__init__(source, volume)
       self.data = data
       self.title = data.get('title')
       self.url = data.get('url')
   @classmethod
   async def from_url(cls, url, *, loop=None, stream=False):
       loop = loop or asyncio.get_event_loop()
       data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
       if 'entries' in data:
           data = data['entries'][0]
       filename = data['url'] if stream else ytdl.prepare_filename(data)
       return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command()
async def join(ctx):
   if not ctx.message.author.voice:
       await ctx.send(f'{ctx.message.author.name} is not connected to a voice channel.')
       return
   else:
       channel = ctx.message.author.voice.channel
   await channel.connect()
@bot.command()
async def leave(ctx):
   if ctx.voice_client:
       await ctx.guild.voice_client.disconnect()
   else:
       await ctx.send("The bot is not connected to a voice channel.")
@bot.command()
async def play(ctx, *, url):
   async with ctx.typing():
       player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
       ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
       await ctx.send(f'Now playing: {player.title}')
@bot.command()
async def pause(ctx):
   ctx.voice_client.pause()
   await ctx.send("Paused the audio.")
@bot.command()
async def resume(ctx):
   ctx.voice_client.resume()
   await ctx.send("Resumed the audio.")
@bot.command()
async def stop(ctx):
   ctx.voice_client.stop()
   await ctx.send("Stopped the audio.")
@bot.command()
async def skip(ctx):
   ctx.voice_client.stop()
   await ctx.send("Skipped the current audio.")





@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')



@bot.command()
async def chat(ctx, *, message: str):
    try:
        response = await get_gpt_response(message)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f'Error: {e}')


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="MeAndMyBot's server")
    if channel:
        await channel.send(f"Welcome to {member.guild.name}, {member.mention}!")


@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="important-messages")
    if channel:
        await channel.send(f"{member.mention} has left {member.guild.name}. Goodbye!")


@ bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
        return
    if message.content.startswith(command_prefix):
        await bot.process_commands(message)
    else:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message,user_message)

@bot.command()
async def roll(ctx):
    roll = randint(1,6)
    embed = discord.Embed(description=f'{ctx.author.name} rolled {roll}', color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def inspire(ctx):
    quote = get_quote()
    embed = discord.Embed(description=quote, color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def on_this_day(ctx):
    event = get_random_event()
    embed = discord.Embed(description=event, color=0x00ff00)
    await ctx.send(embed=embed)


# Define the exchange command
@bot.command()
async def exchange(ctx, base_currency: str, target_currency: str):
   try:
       exchange_rate = get_exchange_rates(base_currency.upper(), target_currency.upper())
       exchange_embed = discord.Embed(title="EXCHANGE RATE", description="Current currency conversion rate", color=0x00ff00)
       exchange_embed.add_field(name="Base Currency", value=base_currency.upper(), inline=True)
       exchange_embed.add_field(name="Target Currency", value=target_currency.upper(), inline=True)
       exchange_embed.add_field(name="Conversion Rate", value=f"{exchange_rate}", inline=False)
       exchange_embed.set_footer(text=f'Requested by {ctx.author.name}.', icon_url=ctx.author.avatar)
       await ctx.send(embed=exchange_embed)
   except Exception as e:
       await ctx.send(f'Error fetching exchange rate: {e}')


@bot.command()
async def ping(ctx):
    latency = bot.latency
    embed = discord.Embed(description=f"{latency * 1000:.2f} ms", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def meme(ctx, *, query: str):
    try:
        gif_url = get_meme(query)
        embed = discord.Embed(title='Meme', color=0x00ff00)
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f'Error fetching meme: {e}')

@bot.command()
async def randommeme(ctx):
    try:
        gif_url = get_random_meme()
        embed = discord.Embed(title='Meme', color=0x00ff00)
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f'Error fetching meme: {e}')


@bot.command(name='hangman')
async def hangman(ctx):
    game = HangmanGame()
    games[ctx.author.id] = game
    await ctx.send("Welcome to Hangman! Guess the word.\n\n" + game.get_status()[2] + "\n" + game.get_display_word())


@bot.command(name='guess')
async def guess(ctx, letter: str):
    game = games.get(ctx.author.id)

    if not game:
        await ctx.send("Start a game first by using the `!hangman` command.")
        return

    if game.completed:
        await ctx.send("This game is over. Start a new game by using the `!hangman` command.")
        return

    response = game.guess(letter.lower())
    display_word, mistakes, hangman_pic = game.get_status()

    await ctx.send(f"{response}\n\n{hangman_pic}\n{display_word}")

    if game.completed:
        del games[ctx.author.id]

@bot.command(name='functions')
async def functions(ctx):
    function_list = """
    **Available Commands:**
    
    `!join` - Join the voice channel you are in.
    `!leave` - Leave the voice channel.
    `!play [url]` - Play audio from a YouTube URL.
    `!pause` - Pause the audio.
    `!resume` - Resume the paused audio.
    `!stop` - Stop the audio.
    `!skip` - Skip the current audio.
    `!chat [message]` - Get a response from the GPT-3.5 chatbot.
    `!roll` - Roll a six-sided die.
    `!inspire` - Get an inspirational quote.
    `!on_this_day` - Get a random historical event that happened on this day.
    `!exchange [base_currency] [target_currency]` - Get the current exchange rate between two currencies.
    `!ping` - Get the bot's latency.
    `!meme [query]` - Get a meme based on the search query.
    `!randommeme` - Get a random meme.
    `!hangman` - Start a game of Hangman.
    `!guess [letter]` - Make a guess in the Hangman game.
    """

    embed = discord.Embed(title="Bot Functions", description=function_list, color=0x00ff00)
    await ctx.send(embed=embed)



def main() -> None:
    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()