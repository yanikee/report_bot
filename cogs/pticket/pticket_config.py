from discord.ext import commands
from discord import app_commands
import discord
import os
import json



class PrivateTicketConfig(commands.GroupCog, group_name='pticket'):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="config", description='匿名ticket開始のボタンを設置するチャンネルで実行してください。')
  @app_commands.describe(config_channel='ticketが送信されるチャンネルを指定')
  async def pticket_config(self, interaction:discord.Interaction, config_channel:discord.TextChannel):
    if not interaction.channel.permissions_for(interaction.user).manage_channels:
      await interaction.response.send_message("権限不足です。\n`チャンネル管理`の権限が必要です。", ephemeral=True)
      return

    await interaction.response.defer(ephemeral=True)
    # 閲覧権限など追加する。
    button_channel = interaction.channel
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
      await interaction.followup.send(embed=embed, ephemeral=True)
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
    button_1 = discord.ui.Button(label="内容を編集する", emoji="✍️", custom_id=f"edit_private_ticket", style=discord.ButtonStyle.primary)
    button_2 = discord.ui.Button(label="確定する", emoji="👌", custom_id=f"confirm_private_ticket", style=discord.ButtonStyle.red)
    button_3 = discord.ui.Button(label="匿名ticket", emoji="🔖", custom_id=f"private_ticket", style=discord.ButtonStyle.primary, disable=True)
    view.add_item(button_1)
    view.add_item(button_2)
    view.add_item(button_3)

    await interaction.followup.send(embed=embed, view=view)


  @commands.Cog.listener()
  async def on_interaction(self, interaction):
    try:
      if not interaction.data["custom_id"] in ["edit_private_ticket", "confirm_private_ticket"]:
        return
    except KeyError:
      return

    if interaction.data["custom_id"] == "edit_private_ticket":
      modal = EditPrivateModal(interaction.message)


class EditPrivateModal(discord.ui.Modal):
  def __init__(self, msg):
    super().__init__(title=f'匿名ticketメッセージ編集モーダル')
    self.bot = bot

    self.private_ticket_msg = discord.ui.TextInput(
      label="",
      style=discord.TextStyle.long,
      default=None,
      placeholder="匿名ticketを開きます。\nこのbotのDMを通じて匿名でサーバー管理者と会話することができます。",
      required=True,
      row=0
    )
    self.add_item(self.private_ticket_msg)

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer()
    # embedの定義
    embed = msg.embeds[0]




async def setup(bot):
  await bot.add_cog(PrivateTicketConfig(bot))