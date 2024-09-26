import discord

import os
import json
import aiofiles
import datetime



def user_cooldown(user_id: int, user_cooldowns: dict, rate:int=30):
  current_time = int(datetime.datetime.now().timestamp())

  if str(user_id) in user_cooldowns:
    retry_after = user_cooldowns[str(user_id)] - current_time

    if retry_after > 0:
      retry_minute = int(retry_after) // 60
      retry_second = int(retry_after) % 60
      embed = discord.Embed(
        title=f"Cooldown",
        description=f"クールダウン中です。\nあと{retry_minute}分{retry_second}秒お待ち下さい。",
        color=0xF2E700,
      )
      return embed, user_cooldowns

    else:
      user_cooldowns.pop(str(user_id))

  user_cooldowns[str(user_id)] = current_time + rate
  return None, user_cooldowns


async def is_server_block(guild:discord.guild, user_id):
  path = f"data/server_block/{guild.id}.json"
  if os.path.exists(path):
    async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
      contents = await f.read()
    server_block_data = json.loads(contents)
  else:
    server_block_data = {}

  if server_block_data.get(str(user_id)):
    return True
  else:
    return False