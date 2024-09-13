import discord

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