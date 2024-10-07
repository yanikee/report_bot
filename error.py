import discord
import aiofiles
import json



async def generate(code:str, additional_desc:str=None, la:str="ja"):
  async with aiofiles.open("messages/error.json", encoding='utf-8', mode="r") as f:
    contents = await f.read()
  error = json.loads(contents)

  match code[0]:
    case "1":
      error_dict = error["manage"]
    case "2":
      error_dict = error["pticket"]
    case "3":
      error_dict = error["report"]
    case _:
      return discord.Embed(description="None")

  if additional_desc:
    desc = f"{error_dict[code][la]}\n{additional_desc}\n\n- エラーガイドは[こちら](https://yanikee.github.io/report_bot-docs2/docs/error/)\n- サポートサーバーは[こちら](https://discord.gg/djQHvM6PtE)"
  else:
    desc = f"{error_dict[code][la]}\n\n- エラーガイドは[こちら](https://yanikee.github.io/report_bot-docs2/docs/error/)\n- サポートサーバーは[こちら](https://discord.gg/djQHvM6PtE)"


  embed=discord.Embed(
    title=f"ERROR[{code}]",
    description=desc,
    color=0xF2E700,
  )

  return embed
