import os
import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv
from uuid import uuid4 as uuid
import hashlib
import random
import json
import asyncio
import requests

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
    [os.remove(os.path.join('temp', f)) for f in os.listdir('temp')]


def load_responses(url):
    response = requests.get(url)
    if response.status_code == 200:
        response_list = json.loads(response.content)["responses"]
        return response_list
    else:
        print(f"Error loading responses: {response.status_code}")
        return []
    
responses = load_responses("https://gist.githubusercontent.com/mishalhossin/dd2296aa6c5fb1518df2bd5266193594/raw/41e69dd4b53d691d22839da5e5e4ea36440aba7e/responses.json")
print(f"Loaded {len(responses)} responses")
dns_resolver = aiohttp.resolver.AsyncResolver(nameservers=["1.1.1.1"])
@bot.hybrid_command(name="upload", description="Upload a file to anonfiles")
async def upload(ctx, attachment: discord.Attachment):
    await ctx.defer()
    response = random.choice(responses)
    message = await ctx.send(f"🤔")
    response_chunks = [response[i:i+25] for i in range(0, len(response), 25)]
    current_chunk = ""
    for chunk in response_chunks:
        current_chunk = current_chunk + chunk
        await message.edit(content=f"{current_chunk}")
    await asyncio.sleep(0.3)
    file_data = await attachment.read()
    random_uuid = uuid()
    file_name = f"{random_uuid}_{attachment.filename}"
    print("\033[32m" + f"Uploading file {file_name}" + "\033[0m")
    await message.edit(content=f"Using filename {file_name}\n")
    await message.edit(content=f"Calculating file hash")
    sha256_hash = hashlib.sha256(file_data)
    hash_value = sha256_hash.hexdigest()
    await message.edit(content=f"File hash: {hash_value}")
    temp_file_path = os.path.join("temp", file_name)
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(file_data)
    try:
        with open(temp_file_path, "rb") as file:
            await message.edit(content=f"Trying to upload file...")
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(resolver=dns_resolver)) as session:
                async with session.post("https://api.anonfiles.com/upload", data={"file": file}) as response:
                    result = await response.json()
                    if result['status']:
                        file_url = result['data']['file']['url']['full']
                        file_size = result['data']['file']['metadata']['size']['readable']
                        embed = discord.Embed(title="Upload Result", color=discord.Color.random())
                        embed.add_field(name="File Hash (sha256)", value=hash_value, inline=False)
                        embed.add_field(name="File Name", value=file_name, inline=False)
                        embed.add_field(name="File Size", value=f"{file_size} bytes", inline=False)
                        embed.add_field(name="File URL", value=file_url, inline=False)
                        await message.edit(content="", embed=embed)
                    else:
                        error_message = result['error']['message']
                        embed = discord.Embed(title="Upload Result", color=0xff0000)
                        embed.add_field(name="Error Message", value=error_message, inline=False)
                        await message.edit(content="", embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Upload failed", color=0xff0000)
        embed.add_field(name="Error Message", value=str(e), inline=False)
        await message.edit(content="", embed=embed)
    os.remove(temp_file_path)
                
if __name__ == "__main__":
    bot.run(TOKEN)
