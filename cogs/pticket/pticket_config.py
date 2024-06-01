from discord.ext import commands
from discord import app_commands
import discord
import os
import json



class PrivateTicketConfig(commands.GroupCog, group_name='pticket'):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="config", description='匿名ticketのボタンを設置, ticket送信チャンネルの設定')
  @app_commands.describe(config_channel='ticket送信チャンネル')
  @app_commands.describe(button_channel='ボタンを送信するチャンネル')
  async def pticket_config(self, interaction:discord.Interaction, config_channel:discord.TextChannel, button_channel:discord.TextChannel):
    if not interaction.channel.permissions_for(interaction.user).manage_channels:
      await interaction.response.send_message("権限不足です。\n`チャンネル管理`の権限が必要です。", ephemeral=True)
      return

    # 閲覧権限など追加する。
    permission_l = []
    cannot = False
    bot_member = interaction.guild.me
    if config_channel.permissions_for(bot_member).read_messages and button_channel.permissions_for(bot_member).read_messages:
      permission_l.append(":white_check_mark:メッセージを見る")
    else:
      permission_l.append(":x:メッセージを見る")
      cannot = True

    if config_channel.permissions_for(bot_member).send_messages and button_channel.permissions_for(bot_member).send_messages:
      permission_l.append(":white_check_mark:メッセージを送信")
    else:
      permission_l.append(":x:メッセージを送信")
      cannot = True

    if config_channel.permissions_for(bot_member).create_public_threads and button_channel.permissions_for(bot_member).create_public_threads:
      permission_l.append(":white_check_mark:公開スレッドの作成")
    else:
      permission_l.append(":x:公開スレッドの作成")
      cannot = True

    if cannot:
      embed=discord.Embed(
        description=f":x:の付いた権限が不足しています。チャンネル設定から権限を追加し、もう一度このコマンドを実行してください。\n**全て:x:の場合report_botのロールをチャンネル権限に追加し、`メッセージを見る`を追加すれば、解決する場合が多い**です。\n\n- " + "\n- ".join(permission_l),
        color=0x9AC9FF
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return


    # 保存
    path = f"data/pticket/guilds/{interaction.guild.id}.json"
    if os.path.exists(path):
      with open(path, encoding='utf-8', mode="r") as f:
        pticket_dict = json.load(f)
      pticket_dict["report_send_channel"] = config_channel.id
    else:
      pticket_dict = {
        "report_send_channel": config_channel.id,
        "pticket_num": 0
      }

    with open(path, mode="w") as f:
      json.dump(pticket_dict, f, indent=2, ensure_ascii=False)

    # buttonを送信
    embed=discord.Embed(
      description="匿名ticketを開きます。\nこのbotのDMを通じて匿名でサーバー管理者と会話することができます。",
      color=0x9AC9FF,
    )
    view = discord.ui.View()
    button = discord.ui.Button(label="匿名ticket", emoji="🔖", custom_id=f"private_ticket", style=discord.ButtonStyle.primary)
    view.add_item(button)

    msg = await button_channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"匿名ticket送信チャンネル：{config_channel.mention}\nbutton：{msg.jump_url}")



async def setup(bot):
  await bot.add_cog(PrivateTicketConfig(bot))