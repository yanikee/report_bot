from discord.ext import commands
from discord import app_commands
import discord
import aiofiles
import json
import os
import error



class ServerBlock(commands.GroupCog, group_name='server'):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="block", description='匿名Report, 匿名Ticketをブロック/ブロック解除します。')
  async def block(self, interaction:discord.Interaction):
    if interaction.channel.type != discord.ChannelType.public_thread:
      embed = error.generate(
        code="1-2-01",
        description="匿名Report, 匿名Ticketのスレッド内で実行してください。",
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

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
      report_dict = None

    if os.path.exists(pticket_path):
      async with aiofiles.open(pticket_path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      pticket_dict = json.loads(contents)
    else:
      pticket_dict = None

    if not report_dict and not pticket_dict:
      embed = error.generate(
        code="1-2-02",
        description="このスレッドは匿名Report, 匿名Ticketのスレッドではありません。",
      )
      await interaction.followup.send(embed=embed, ephemeral=True)
      return

    # reportの場合
    if str(interaction.channel.id) in report_dict:
      data_dict = report_dict
    # pticketの場合
    elif str(interaction.channel.id) in pticket_dict:
      data_dict = pticket_dict
    else:
      embed = error.generate(
        code="1-2-03",
        description="このスレッドは匿名Report, 匿名Ticketのスレッドではありません。",
      )
      await interaction.followup.send(embed=embed, ephemeral=True)
      return

    # user_id, userを取得
    user_id = data_dict.get(str(interaction.channel.id))
    user = await interaction.guild.fetch_member(int(user_id))

    # server_blockを取得
    path = f"data/server_block/{interaction.guild.id}.json"
    if os.path.exists(path):
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      server_block_data = json.loads(contents)
    else:
      server_block_data = {}

    # blockedのbool
    block_bool = server_block_data.get(str(user_id))
    if block_bool:
      server_block_data[str(user_id)] = False
    else:
      server_block_data[str(user_id)] = True

    # 保存
    contents = json.dumps(server_block_data, indent=2, ensure_ascii=False)
    async with aiofiles.open(path, encoding='utf-8', mode="w") as f:
      await f.write(contents)

    # 最後に送信, blockされた人にも送信
    if server_block_data[str(user_id)]:
      embed = discord.Embed(
        description="ユーザをサーバーブロックしています。\nこのユーザーはこのサーバー内で本botの全ての機能を利用できません。\nサーバーブロックを解除する -> `/block server`",
        color=0xff0000,
      )
      embed.set_footer(
        text=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
      )

      user_embed = discord.Embed(
        description=f"あなたは『{interaction.guild.name}』の管理者によってサーバーブロックされました。\nこのサーバー内では本botの全ての機能をご利用いただけません。",
        color=0xff0000,
      )
      user_embed.set_footer(
        text=interaction.guild.name,
        icon_url=interaction.guild.icon.url,
      )

    else:
      embed = discord.Embed(
        description="このユーザーのサーバーブロックを解除しました。",
        color=0xff0000,
      )
      embed.set_footer(
        text=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
      )

      user_embed = discord.Embed(
        description=f"『{interaction.guild.name}』のサーバーブロックが解除されました。",
        color=0xff0000,
      )
      user_embed.set_footer(
        text=interaction.guild.name,
        icon_url=interaction.guild.icon.url,
      )

    await interaction.channel.send(embed=embed)
    await user.send(embed=user_embed)
    await interaction.response.send_message("ブロック完了", ephemeral=True)



async def setup(bot):
  await bot.add_cog(ServerBlock(bot))