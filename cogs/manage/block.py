from discord.ext import commands
from discord import app_commands
import discord
import aiofiles
import json
import os
import error



class Block(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="block", description='匿名Report, 匿名Ticketをブロック/ブロック解除します。')
  async def block(self, interaction:discord.Interaction):
    if interaction.channel.type != discord.ChannelType.public_thread:
      embed = error.generate(
        code="1-1-01",
        description="匿名Report, 匿名Ticketのスレッド内で実行してください。",
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    await interaction.response.defer(ephemeral=True)

    # report_dict, pticket_dictを取得する
    # 取得できなかった場合->return
    report_path = f"data/report/private_report/{interaction.guild.id}.json"
    pticket_path = f"data/pticket/pticket/{interaction.guild.id}.json"
    count = 0

    if os.path.exists(report_path):
      async with aiofiles.open(report_path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      report_dict = json.loads(contents)
    else:
      report_dict = ""

    if os.path.exists(pticket_path):
      async with aiofiles.open(pticket_path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      pticket_dict = json.loads(contents)
    else:
      pticket_dict = ""

    if not report_dict and not pticket_dict:
      embed = error.generate(
        code="1-1-02",
        description="このスレッドは匿名Report, 匿名Ticketのスレッドではありません。",
      )
      await interaction.followup.send(embed=embed, ephemeral=True)
      return


    # reportの場合
    if str(interaction.channel.id) in report_dict:
      blocked_path = f"data/report/blocked/{interaction.guild.id}.json"
    # pticketの場合
    elif str(interaction.channel.id) in pticket_dict:
      blocked_path = f"data/pticket/blocked/{interaction.guild.id}.json"
    else:
      embed = error.generate(
        code="1-1-03",
        description="このスレッドは匿名Report, 匿名Ticketのスレッドではありません。",
      )
      await interaction.followup.send(embed=embed, ephemeral=True)
      return

    # blocked_dictを定義
    if os.path.exists(blocked_path):
      async with aiofiles.open(blocked_path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      blocked_dict = json.loads(contents)
    else:
      blocked_dict = {}

    # blockedのbool
    try:
      if blocked_dict[str(interaction.channel.id)] == True:
        blocked_dict[str(interaction.channel.id)] = False
      else:
        blocked_dict[str(interaction.channel.id)] = True
    except KeyError:
      blocked_dict[str(interaction.channel.id)] = True

    # 保存
    contents = json.dumps(blocked_dict, indent=2, ensure_ascii=False)
    async with aiofiles.open(blocked_path, encoding='utf-8', mode="w") as f:
      await f.write(contents)

    # 最後に送信
    if blocked_dict[str(interaction.channel.id)] == True:
      embed = discord.Embed(
        description="ユーザーからの返信をブロックしています。\nブロックを解除する -> `/block`",
        color=0xff0000,
      )
      embed.set_footer(
        text=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
      )
      await interaction.followup.send("ユーザーのブロックが完了しました。\nブロックを解除するには、もう一度`/block`コマンドを実行してください。", ephemeral=True)

    else:
      embed = discord.Embed(
        description="ブロックを解除しました。",
        color=0xff0000,
      )
      embed.set_footer(
        text=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
      )
      await interaction.followup.send("ユーザーのブロックを解除しました。", ephemeral=True)

    await interaction.channel.send(embed=embed)



async def setup(bot):
  await bot.add_cog(Block(bot))