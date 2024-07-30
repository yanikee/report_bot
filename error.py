import discord

def generate(code:str, description:str, support:bool=True):
  if support:
    desc = f"{description}\n\n- サポートサーバーは[こちら](https://discord.gg/djQHvM6PtE)"
  else:
    desc = description

  embed=discord.Embed(
    title=f"ERROR[{code}]",
    description=desc,
    color=0xF2E700,
  )

  return embed
