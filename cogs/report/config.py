from discord.ext import commands
from discord import app_commands
import discord
import os
import json
import aiofiles
import error



class ReportConfig(commands.GroupCog, group_name='report'):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="config", description='"report"を送信するチャンネルを設定します。')
  @app_commands.describe(channel='"report"を送信するチャンネル')
  async def report_config(self, interaction:discord.Interaction, channel:discord.TextChannel=None):
    if not interaction.channel.permissions_for(interaction.user).manage_channels:
      embed=error.generate(
        code="3-1-01",
        description=f"権限不足です。\n`チャンネル管理`の権限が必要です。",
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    if not channel:
      channel = interaction.channel

    if channel.type != discord.ChannelType.text:
      embed=error.generate(
        code="3-1-02",
        description=f"テキストチャンネルのみ設定可能です。",
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    # 閲覧権限など追加する。
    permission_l = []
    cannot = False
    bot_member = interaction.guild.me
    if channel.permissions_for(bot_member).read_messages:
      permission_l.append(":white_check_mark:メッセージを見る")
    else:
      permission_l.append(":x:メッセージを見る")
      cannot = True

    if channel.permissions_for(bot_member).send_messages:
      permission_l.append(":white_check_mark:メッセージを送信")
    else:
      permission_l.append(":x:メッセージを送信")
      cannot = True

    if channel.permissions_for(bot_member).create_public_threads:
      permission_l.append(":white_check_mark:公開スレッドの作成")
    else:
      permission_l.append(":x:公開スレッドの作成")
      cannot = True

    if cannot:
      embed=error.generate(
        code="3-1-03",
        description=f":x:の付いた権限が不足しています。チャンネル設定から権限を追加し、もう一度このコマンドを実行してください。\n"
                    "全て:x:の場合、**チャンネル権限にreport bot!のロールを追加し、「メッセージを見る」を付与**すれば、解決することが多いです。"
                    "\n\n- " + "\n- ".join(permission_l)
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    # 保存
    path = f"data/report/guilds/{interaction.guild.id}.json"
    if os.path.exists(path):
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      report_dict = json.loads(contents)
      report_dict["report_send_channel"] = channel.id

    else:
      report_dict = {
        "report_send_channel": channel.id,
        "reply_num": 0
      }

    async with aiofiles.open(path, mode="w") as f:
      contents = json.dumps(report_dict, indent=2, ensure_ascii=False)
      await f.write(contents)

    embed = discord.Embed(
      description=f'"report"を{channel.mention}に送信します。',
      color=0xF4BD44,
    )
    await interaction.response.send_message(embed=embed)



async def setup(bot):
  await bot.add_cog(ReportConfig(bot))