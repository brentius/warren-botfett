'''
inputs: discord token, allowed id, inbound messages
outputs: commands, push messages
'''

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
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("testing"):
        await message.channel.send(f"I am {client.user}")

client.run(BOT_TOKEN)
