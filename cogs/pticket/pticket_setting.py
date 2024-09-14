from discord.ext import commands
from discord import app_commands
import discord
import os
import json
import aiofiles
import error



class PrivateTicketConfig(commands.GroupCog, group_name='pticket'):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="setting", description='匿名Ticket開始ボタンを設置するチャンネルで実行してください。')
  @app_commands.describe(ticket_channel='Ticketが送信されるチャンネルを指定します')
  @app_commands.describe(mention_role="Ticketが送信されたときにメンションするロールを指定します")
  async def pticket_setting(self, interaction:discord.Interaction, ticket_channel:discord.TextChannel, mention_role:discord.Role=None):
    if not interaction.channel.permissions_for(interaction.user).manage_channels:
      embed=error.generate(
        code="2-1-01",
        description=f"権限不足です。\n`チャンネル管理`の権限が必要です。",
      )
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    await interaction.response.defer(ephemeral=True)
    # 閲覧権限など追加する。
    button_channel = interaction.channel
    permission_l = []
    cannot = False
    bot_member = interaction.guild.me
    if ticket_channel.permissions_for(bot_member).read_messages and button_channel.permissions_for(bot_member).read_messages:
      permission_l.append(":white_check_mark:メッセージを見る")
    else:
      permission_l.append(":x:メッセージを見る")
      cannot = True

    if ticket_channel.permissions_for(bot_member).send_messages and button_channel.permissions_for(bot_member).send_messages:
      permission_l.append(":white_check_mark:メッセージを送信")
    else:
      permission_l.append(":x:メッセージを送信")
      cannot = True

    if ticket_channel.permissions_for(bot_member).create_public_threads and button_channel.permissions_for(bot_member).create_public_threads:
      permission_l.append(":white_check_mark:公開スレッドの作成")
    else:
      permission_l.append(":x:公開スレッドの作成")
      cannot = True

    if cannot:
      embed=error.generate(
        code="2-1-02",
        description=f":x:の付いた権限が不足しています。チャンネル設定から権限を追加し、もう一度このコマンドを実行してください。\n"
                    "全て:x:の場合、**チャンネル権限にreport bot!のロールを追加し、「メッセージを見る」を付与**すれば、解決することが多いです。\n\n"
                    "このチャンネルと、Ticketが送信されるチャンネルの2つの権限をご確認ください。"
                    "\n\n- " + "\n- ".join(permission_l)
      )
      await interaction.followup.send(embed=embed, ephemeral=True)
      return


    # 保存
    path = f"data/pticket/guilds/{interaction.guild.id}.json"
    if os.path.exists(path):
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      pticket_dict = json.loads(contents)
      pticket_dict["report_send_channel"] = ticket_channel.id
    else:
      pticket_dict = {
        "report_send_channel": ticket_channel.id,
        "pticket_num": 0
      }
    if mention_role:
      pticket_dict["mention_role"] = mention_role.id
    else:
      pticket_dict["mention_role"] = None

    async with aiofiles.open(path, mode="w") as f:
      contents = json.dumps(pticket_dict, indent=2, ensure_ascii=False)
      await f.write(contents)

    # Ticketチャンネルに確認メッセージを送信
    if mention_role:
      description=f'開始ボタンチャンネル：{interaction.channel.mention}\n送信チャンネル：{ticket_channel.mention}\nメンションロール：{mention_role.mention}'
    else:
      description=f'開始ボタンチャンネル：{interaction.channel.mention}\n送信チャンネル：{ticket_channel.mention}\nメンションロール：なし'

    embed = discord.Embed(
      title="Ticket",
      description=description,
      color=0x9AC9FF,
    )
    await ticket_channel.send(embed=embed)

    # buttonを送信
    embed=discord.Embed(
      title="匿名Ticket",
      description="匿名Ticketを開きます。\nこのbotのDMを通じて匿名でサーバー管理者と会話することができます。",
      color=0x9AC9FF,
    )
    embed.set_footer(
      text="＊下のボタンから匿名Ticket開始パネルのメッセージを編集することができます。"
    )
    view = discord.ui.View()
    button_0 = discord.ui.Button(label="匿名Ticket", emoji="🔖", custom_id=f"private_ticket", style=discord.ButtonStyle.primary, disabled=True, row=0)
    button_1 = discord.ui.Button(label="内容を編集する", emoji="✍️", custom_id=f"edit_private_ticket", style=discord.ButtonStyle.green, row=1)
    button_2 = discord.ui.Button(label="確定する", emoji="👌", custom_id=f"confirm_private_ticket", style=discord.ButtonStyle.red, row=1)
    view.add_item(button_0)
    view.add_item(button_1)
    view.add_item(button_2)

    await interaction.followup.send(embed=embed, view=view, ephemeral=True)


  @commands.Cog.listener()
  async def on_interaction(self, interaction):
    try:
      if not interaction.data["custom_id"] in ["edit_private_ticket", "confirm_private_ticket"]:
        return
    except KeyError:
      return


    # 確定ボタンを押したとき
    if interaction.data["custom_id"] == "confirm_private_ticket":
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="匿名Ticket", emoji="🔖", custom_id=f"private_ticket", style=discord.ButtonStyle.primary, disabled=False, row=0)
      view.add_item(button_0)
      await interaction.response.edit_message(content="ok", embed=None, view=None)
      # フッターを消し、送信する
      embed = interaction.message.embeds[0]
      embed.set_footer(text=None)
      await interaction.channel.send(embed=embed, view=view)

    # 編集ボタンを押したとき
    elif interaction.data["custom_id"] == "edit_private_ticket":
      modal = EditPrivateModal(interaction.message)
      await interaction.response.send_modal(modal)


# パネル編集
class EditPrivateModal(discord.ui.Modal):
  def __init__(self, msg):
    super().__init__(title=f'匿名Ticket開始パネル 編集モーダル')
    self.msg = msg

    self.private_ticket_msg = discord.ui.TextInput(
      label="パネルに表示する内容を入力してください。",
      style=discord.TextStyle.long,
      default=msg.embeds[0].description,
      required=True,
      row=0
    )
    self.add_item(self.private_ticket_msg)

  async def on_submit(self, interaction: discord.Interaction):
    # embedの定義
    embed = interaction.message.embeds[0]
    embed.description = self.private_ticket_msg.value

    # 編集パネルの変更
    await interaction.response.edit_message(embed=embed)



async def setup(bot):
  await bot.add_cog(PrivateTicketConfig(bot))