import discord
import aiofiles
import json



async def generate(cog_type:str, code:str, description:str, la:str="ja"):
  async with aiofiles.open("error.json", encoding='utf-8', mode="r") as f:
    contents = await f.read()
  error = json.loads(contents)

  if cog_type == "manage":
    error_dict = error["manage"]
  elif cog_type == "ticket":
    error_dict = error["ticket"]
  elif cog_type == "report":
    error_dict = error["report"]
  else:
    return 0

  desc = f"{error_dict[code][la]}\n\n- エラーガイドは[こちら](https://yanikee.github.io/report_bot-docs2/docs/error/)\n- サポートサーバーは[こちら](https://discord.gg/djQHvM6PtE)"

  embed=discord.Embed(
    title=f"ERROR[{code}]",
    description=desc,
    color=0xF2E700,
  )

  return embed
