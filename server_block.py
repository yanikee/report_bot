import discord
import os
import aiofiles
import json



async def is_server_block(interaction:discord.Interaction=None, message:discord.message=None):
  path = f"data/server_block/{interaction.guild.id}.json"
  if os.path.exists(path):
    async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
      contents = await f.read()
    server_block_data = json.loads(contents)
  else:
    server_block_data = {}