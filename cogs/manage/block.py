from discord.ext import commands
from discord import app_commands
import discord
import aiofiles


class Block(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="block", description='匿名Report, 匿名Ticketをブロック/ブロック解除します。')
  async def block(self, interaction:discord.Interaction):
    if interaction.channel.type != discord.ChannelType.public_thread:
      await interaction.response.send_message("匿名Report, 匿名Ticketのスレッド内で実行してください。", ephemeral=True)
      return

    await interaction.response.defer(ephemeral=True)

    report_path = f"data/report/report/{interaction.channel.id}.json"
    pticket_path = f"data/pticket/pticket/{interaction.channel.id}.json"

    # 匿名reportだった場合
    if os.path.exists(report_path):
      async with aiofiles.open(report_path, encoding='utf-8', mode="f") as f:
        contents = await f.read()

      report_dict = self.bool_change(json.loads(contents))

      async with aiofiles.open(report_path, encoding='utf-8', mode="w") as f:
        contents = json.dumps(report_dict, indent=2, ensure_ascii=False)
        await f.write(contents)

    # 匿名Ticketだった場合
    elif os.path.exists(pticket_path):
      async with aiofiles.open(pticklet_path, encoding='utf-8', mode="f") as f:
        contents = await f.read()

      pticket_dict = self.bool_change(json.loads(contents))

      async with aiofiles.open(pticket_path, encoding='utf-8', mode="w") as f:
        contents = json.dumps(pticket_dict, indent=2, ensure_ascii=False)
        await f.write(contents)

    # データが見つからなかった場合
    else:
      await interaction.followup.send("保存データが見つかりませんでした。", ephemeral=True)
      error=f"[ERROR]\nGuild_id : {interaction.guild.id}\nChannel_id : {interaction.channel.id}\n"
      print(error)
      return


    await interaction.followup.send("ブロックが完了しました。\n以後、ユーザーからメッセージが届かなくなります。", ephemeral=True)


  # blockのboolを変更する関数
  def bool_change(self, data_dict):
    try:
      if data_dict["blocked"] == True:
        data_dict["blocked"] = False
      else:
        data_dict["blocked"] = True
    except KeyError:
      data_dict["blocked"] = True

    return data_dict



async def setup(bot):
  await bot.add_cog(Block(bot))