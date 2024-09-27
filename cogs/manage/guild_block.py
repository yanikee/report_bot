from discord.ext import commands
from discord import app_commands
import discord
import aiofiles
import json
import os
import error



class GuildBlock(commands.GroupCog, group_name='server'):
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
      report_dict = ""

    if os.path.exists(pticket_path):
      async with aiofiles.open(pticket_path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      pticket_dict = json.loads(contents)
    else:
      pticket_dict = ""

    if not report_dict and not pticket_dict:
      embed = error.generate(
        code="1-2-02",
        description="このスレッドは匿名Report, 匿名Ticketのスレッドではありません。",
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    # reportの場合
    if str(interaction.channel.id) in report_dict:
      case_type = "Report"
      data_dict = report_dict
    # pticketの場合
    elif str(interaction.channel.id) in pticket_dict:
      case_type = "Ticket"
      data_dict = pticket_dict
    else:
      embed = error.generate(
        code="1-2-03",
        description="このスレッドは匿名Report, 匿名Ticketのスレッドではありません。",
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    # user_id, userを取得
    user_id = data_dict.get(str(interaction.channel.id))
    user = await interaction.guild.fetch_member(int(user_id))

    # guild_blockを取得
    path = f"data/guild_block/{interaction.guild.id}.json"
    if os.path.exists(path):
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      guild_block_data = json.loads(contents)
    else:
      guild_block_data = {}

    # blockedのbool
    block_bool = guild_block_data.get(str(user_id))
    if block_bool:
      guild_block_data[str(user_id)] = False
    else:
      guild_block_data[str(user_id)] = True

    # 保存
    contents = json.dumps(guild_block_data, indent=2, ensure_ascii=False)
    async with aiofiles.open(path, encoding='utf-8', mode="w") as f:
      await f.write(contents)

    # 最後に送信, blockされた人にも送信
    if guild_block_data[str(user_id)]:
      embed = discord.Embed(
        description=f"この匿名{case_type}の報告者をサーバーブロックしています。\nこの報告者はこのサーバー内で本botの全ての機能を利用できません。\nサーバーブロックを解除する -> `/block server`",
        color=0xff0000,
      )
      embed.set_footer(
        text=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None,
      )

      user_embed = discord.Embed(
        description=f"あなたは『{interaction.guild.name}』の管理者によってサーバーブロックされました。\nこのサーバー内では本botの全ての機能をご利用いただけません。",
        color=0xff0000,
      )
      user_embed.set_footer(
        text=interaction.guild.name,
        icon_url=interaction.guild.icon.url if interaction.guild.icon else None,
      )

    else:
      embed = discord.Embed(
        description=f"この匿名{case_type}報告者のサーバーブロックを解除しました。",
        color=0xff0000,
      )
      embed.set_footer(
        text=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None,
      )

      user_embed = discord.Embed(
        description=f"『{interaction.guild.name}』のサーバーブロックが解除されました。",
        color=0xff0000,
      )
      user_embed.set_footer(
        text=interaction.guild.name,
        icon_url=interaction.guild.icon.url if interaction.guild.icon else None,
      )

    await user.send(embed=user_embed)
    await interaction.response.send_message(embed=embed)



async def setup(bot):
  await bot.add_cog(GuildBlock(bot))