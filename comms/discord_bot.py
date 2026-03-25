'''
inputs: discord token, allowed id, inbound messages
outputs: commands, push messages
'''

# This example requires the 'message_content' intent.

import discord
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_ID = os.getenv("DISCORD_APP_ID")
DISCORD_KEY = os.getenv("DISCORD_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')

client.run(BOT_TOKEN)
