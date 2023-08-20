import os
import io
import aiohttp
import discord
import hashlib
import random
import json
import asyncio
import requests
import uuid
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Set up the Discord bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents, heartbeat_timeout=60)
TOKEN = os.getenv('DISCORD_TOKEN')

@bot.event
async def on_ready():
    await bot.tree.sync()
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(),
        scopes=("bot", "applications.commands")
    )
    def print_in_color(text, color):
        return f"\033[{color}m{text}\033[0m"

    if os.name == 'posix':
        os.system('clear')
    if os.name == 'nt':
        os.system('cls')
    
    print(print_in_color(f"{bot.user} aka {bot.user.name} has connected to Discord!", "\033[1;97"))
    print(print_in_color(f"Invite link: {invite_link}", "1;36"))


def load_responses(url):
    response = json.loads(requests.get(url).content)["responses"]
    return response 
    
responses = load_responses("https://gist.githubusercontent.com/mishalhossin/dd2296aa6c5fb1518df2bd5266193594/raw/41e69dd4b53d691d22839da5e5e4ea36440aba7e/responses.json")
print(f"Loaded {len(responses)} responses")

@bot.hybrid_command(name="upload", description="Upload a file")
async def upload(ctx, attachment: discord.Attachment):
    await ctx.defer()
    dns_resolver = aiohttp.resolver.AsyncResolver(nameservers=["1.1.1.1"])
    random_msg = random.choice(responses)
    message = await ctx.send(f"🤔")
    file_data = await attachment.read()
    file_name = f"{attachment.filename}"
    print("\033[32m" + f"Uploading file {file_name}" + "\033[0m")
    
    await message.edit(content=f"Calculating file hash")
    sha256_hash = hashlib.sha256(file_data)
    hash_value = sha256_hash.hexdigest()
    await message.edit(content=f"File hash: {hash_value}")
    bytes_io = io.BytesIO(file_data)
    bytes_size = len(bytes_io.getbuffer())
    file = (file_name, bytes_io)

    try:
        await message.edit(content=f"Trying to upload file...")
        
        data = aiohttp.FormData()
        data.add_field('file', file[1], filename=file[0])
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(resolver=dns_resolver)) as session:
            async with session.post("https://0x0.st", data=data) as response:
                if response.status == 200:
                    file_url = await response.text()
                    is_nsfw = False
                    footer_text = random_msg
                    color = discord.Color.random()
                    if "#nsfw" in file_url:
                        color = 0xff0000
                        footer_text = "⚠️ The uploaded file has been detected to contain content that is not suitable for a work environment or public display. Please be cautious when viewing"
                        is_nsfw = True
                        
                    embed = discord.Embed(title="Upload Result", color=color)
                    embed.add_field(name="File Hash (sha256)", value=hash_value, inline=False)
                    embed.add_field(name="File Name", value=file_name, inline=False)
                    embed.add_field(name="File Size", value=f"{bytes_size} bytes", inline=False)
                    if is_nsfw:
                        embed.add_field(name="File URL", value=f"||{file_url}||", inline=False)
                    else:
                        embed.add_field(name="File URL", value=file_url, inline=False)
                    embed.set_footer(text=footer_text)
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(label="Open File", url=file_url))
                    view.add_item(discord.ui.Button(label="Virus Check", url=f"https://www.virustotal.com/gui/search/{hash_value}"))
                    await message.edit(content="", embed=embed, view=view)
                else:
                    error_message = await response.text()
                    embed = discord.Embed(title="Upload Result", color=0xff0000)
                    embed.add_field(name="Error Message", value=f"```{error_message}```", inline=False)
                    await message.edit(content="", embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Upload failed", color=0xff0000)
        embed.add_field(name="Error Message", value=str(e), inline=False)
        await message.edit(content="", embed=embed)
                
if __name__ == "__main__":
    bot.run(TOKEN)
