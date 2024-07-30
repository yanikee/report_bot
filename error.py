import discord

def generate(num:str, description:str, support:bool=True):
  if support:
    desc = f"{description}\n\n- サポートサーバーは[こちら](https://discord.gg/djQHvM6PtE)"
  else:
    desc = description

  embed=discord.Embed(
    title=f"ERROR[{num}]",
    description=desc,
    color=0xF2E700,
  )

  return embed
