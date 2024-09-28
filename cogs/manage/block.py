from discord.ext import commands
from discord import app_commands
import discord
import aiofiles
import json
import os
import error
from typing import List



class Block(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def block_type(self, interaction: discord.Interaction, _):
    return [app_commands.Choice(name=case_type, value=case_type) for case_type in ["通常block", "サーバーblock"]]

  @app_commands.command(name="block", description='匿名Report, 匿名Ticketをブロック/ブロック解除します。')
  @app_commands.autocomplete(block_type=block_type)
  @app_commands.describe(block_type="通常block：報告者はこのスレッドにのみ返信できなくなる / サーバーブロック：報告者はこのサーバー内の全ての機能が利用できなくなる")
  async def block(self, interaction:discord.Interaction, block_type:str):
    if interaction.channel.type != discord.ChannelType.public_thread:
      embed = error.generate(
        code="1-1-01",
        description="匿名Report, 匿名Ticketのスレッド内で実行してください。",
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    if block_type == "サーバーblock":
      await self.guild_block(interaction=interaction)
    else:
      await self.nomal_block(interaction=interaction)


  async def guild_block(self, interaction:discord.Interaction):
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
        description=f"この匿名{case_type}の報告者をサーバーブロックしています。\nこの報告者はこのサーバー内で本botの全ての機能を利用できません。\nサーバーブロックを解除する -> `/block`",
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


  async def nomal_block(self, interaction:discord.Interaction):
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
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return


    # reportの場合
    if str(interaction.channel.id) in report_dict:
      blocked_path = f"data/report/blocked/{interaction.guild.id}.json"
      case_type = "Report"
    # pticketの場合
    elif str(interaction.channel.id) in pticket_dict:
      blocked_path = f"data/pticket/blocked/{interaction.guild.id}.json"
      case_type = "Ticket"
    else:
      embed = error.generate(
        code="1-1-03",
        description="このスレッドは匿名Report, 匿名Ticketのスレッドではありません。",
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
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
        description=f"この匿名{case_type}報告者からの返信をブロックしています。\nこの報告者はこの匿名{case_type}のみに返信できません。\nブロックを解除する -> `/block`",
        color=0xffcc00,
      )
      embed.set_footer(
        text=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None,
      )

    else:
      embed = discord.Embed(
        description=f"この匿名{case_type}報告者のブロックを解除しました。",
        color=0xffcc00,
      )
      embed.set_footer(
        text=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None,
      )

    await interaction.response.send_message(embed=embed)



async def setup(bot):
  await bot.add_cog(Block(bot))