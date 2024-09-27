from discord.ext import commands
from discord import app_commands
import discord

import aiofiles
import json
import os

import error



class Settings(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="settings", description='設定を行います')
  async def settings(self, interaction:discord.Interaction):
    if not interaction.channel.permissions_for(interaction.user).manage_channels:
      embed = error.generate(
        code="1-5-01",
        description=f"権限不足です。\n`チャンネル管理`の権限が必要です。",
      )
      return await interaction.response.send_message(embed=embed, ephemeral=True)


    # 正しくないidを削除
    for type in ["report", "pticket"]:
      datas = await self.get_data(interaction, type=type)
      for id_int in datas.values():
        channel = interaction.guild.get_channel(id_int)
        role = interaction.guild.get_role(id_int)
        # 両方Falseの場合 -> "reply_num"以外は削除
        if not any([channel, role]):
          datas = {k: v for k, v in datas.items() if (k == "reply_num" or k == "pticket_num" or v != id_int)}

      await self.save_data(interaction, data=datas, type=type)


    embed, view = self.settings_page_1()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


  async def get_data(self, interaction:discord.Interaction, type:str):
    if type == "report":
      path = f"data/report/guilds/{interaction.guild.id}.json"
    else:
      path = f"data/pticket/guilds/{interaction.guild.id}.json"

    if os.path.exists(path):
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      return json.loads(contents)
    else:
      return {}

  async def save_data(self, interaction:discord.Interaction, data:dict, type:str):
    if type == "report":
      path = f"data/report/guilds/{interaction.guild.id}.json"
    else:
      path = f"data/pticket/guilds/{interaction.guild.id}.json"

    contents = json.dumps(data, indent=2, ensure_ascii=False)
    async with aiofiles.open(path, encoding='utf-8', mode="w") as f:
      await f.write(contents)


  def settings_page_1(self):
    embed = discord.Embed(
      title="settings (1/3)",
      description="1. Report機能\n"
                  "1. 匿名Ticket機能\n"
                  "これらの設定を行います",
      color=0xF4BD44,
    )
    view = discord.ui.View()
    button = discord.ui.Button(label="次へ", custom_id=f"settings_page_2", style=discord.ButtonStyle.primary, row=0)
    view.add_item(button)
    return embed, view


  async def settings_page_2(self, interaction:discord.Interaction, error:bool=None):
    data = await self.get_data(interaction, type="report")

    # Embedの定義
    embed = discord.Embed(
      title="settings (2/3)",
      description="## Report機能の設定\n以下の**2つ**の設定を行ってください\n(Report機能を無効化したい場合は、全ての項目を未選択にしてください)",
      color=0xF4BD44,
    )
    embed.add_field(
      name=("🔵" if data.get("report_send_channel") else "⚪") + "Report送信チャンネル",
      value="\n- Reportを送信するチャンネルを設定します\n",
      inline=False
    )
    embed.add_field(
      name=("🔵" if data.get("mention_role") else "⚪") + "Report送信時メンションロール(任意)",
      value="- Reportが送信されたときにメンションするロールを設定します",
      inline=False
    )

    view = discord.ui.View()
    select_0 = discord.ui.ChannelSelect(
      custom_id="settings_select_report_channel",
      channel_types=[discord.ChannelType.text],
      placeholder="Report送信チャンネル",
      min_values=0,
      default_values=[interaction.guild.get_channel(data["report_send_channel"])] if data.get("report_send_channel") else None,
      row=0
    )
    select_1 = discord.ui.RoleSelect(
      custom_id="settings_select_report_mention_role",
      placeholder="Report送信時メンションロール",
      min_values=0,
      default_values=[interaction.guild.get_role(data["mention_role"])] if data.get("mention_role") else None,
      row=1
    )
    view.add_item(select_0)
    view.add_item(select_1)

    button_0 = discord.ui.Button(label="戻る", custom_id=f"settings_page_1", style=discord.ButtonStyle.gray, row=2)
    button_1 = discord.ui.Button(label="次へ", custom_id=f"settings_page_3", style=discord.ButtonStyle.primary, row=2)
    view.add_item(button_0)
    view.add_item(button_1)

    if error:
      await interaction.followup.edit_message(interaction.message.id, view=None)
      await interaction.followup.edit_message(interaction.message.id, embed=embed, view=view)
    else:
      await interaction.response.edit_message(embed=embed, view=view)


  async def settings_page_3(self, interaction:discord.Interaction, error:bool=None):
    data = await self.get_data(interaction,type="pticket")
    embed = discord.Embed(
      title="settings (3/3)",
      description="## 匿名Ticket機能の設定\n以下の**2つ**の設定を行ってください\n(匿名Ticket機能を無効化したい場合は、全ての項目を未選択にしてください)",
      color=0x9AC9FF,
    )
    embed.add_field(
      name=("🔵" if data.get("report_send_channel") else "⚪") + "匿名Ticket送信チャンネル",
      value="- 匿名Ticketを送信するチャンネルを設定します",
      inline=False
    )
    embed.add_field(
      name=("🔵" if data.get("mention_role") else "⚪") + "匿名Ticket送信時メンションロール(任意)",
      value="- 匿名Ticketが送信されたときにメンションするロールを設定します",
      inline=False
    )

    view = discord.ui.View()
    select_0 = discord.ui.ChannelSelect(
      custom_id="settings_select_pticket_channel",
      channel_types=[discord.ChannelType.text],
      placeholder="匿名Ticket送信チャンネル",
      min_values=0,
      default_values=[interaction.guild.get_channel(data["report_send_channel"])] if data.get("report_send_channel") else None,
      row=0
    )
    select_2 = discord.ui.RoleSelect(
      custom_id="settings_select_pticket_mention_role",
      placeholder="匿名Ticket送信時メンションロール",
      min_values=0,
      default_values=[interaction.guild.get_role(data["mention_role"])] if data.get("mention_role") else None,
      row=2
    )
    view.add_item(select_0)
    view.add_item(select_2)

    button_0 = discord.ui.Button(label="戻る", custom_id=f"settings_page_2", style=discord.ButtonStyle.gray, row=3)

    if data.get("report_send_channel"):
      button_1 = discord.ui.Button(label="保存して次へ", custom_id=f"settings_panel_config", style=discord.ButtonStyle.primary, row=3)
    else:
      button_1 = discord.ui.Button(label="保存して終了", custom_id=f"settings_final", style=discord.ButtonStyle.red, row=3)

    view.add_item(button_0)
    view.add_item(button_1)

    if error:
      await interaction.followup.edit_message(interaction.message.id, view=None)
      await interaction.followup.edit_message(interaction.message.id, embed=embed, view=view)
    else:
      await interaction.response.edit_message(embed=embed, view=view)


  async def settings_panel_config(self, interaction:discord.Interaction, error:bool=None, value:str="匿名Ticketを作成します。\nこのbotのDMを通じて匿名でサーバー管理者と会話することができます。"):
    data = await self.get_data(interaction,type="pticket")
    embed_0 = discord.Embed(
      title="settings",
      description="以下の**2つ**の設定を行ってください",
      color=0x9AC9FF,
    )
    embed_0.add_field(
      name=("🔵" if data.get("report_button_channel") else "⚪") + "匿名Ticket作成ボタン設置チャンネル",
      value="- 匿名Ticketを作成するためのボタンを設置するチャンネルを設定します",
      inline=False
    )
    embed_0.add_field(
      name="🔵匿名Ticket作成パネルのメッセージ編集",
      value="- ボタンから匿名Ticket作成パネルのメッセージを編集することができます",
      inline=False
    )

    embed = discord.Embed(
      title="匿名Ticket",
      description=value,
      color=0x9AC9FF,
    )

    embeds = [embed_0, embed]

    view = discord.ui.View()
    select_1 = discord.ui.ChannelSelect(
      custom_id="settings_select_pticket_button_channel",
      channel_types=[discord.ChannelType.text],
      placeholder="匿名Ticket作成ボタン設置チャンネル",
      min_values=0,
      default_values=[interaction.guild.get_channel(data["report_button_channel"])] if data.get("report_button_channel") else None,
      row=0
    )
    view.add_item(select_1)

    button_1 = discord.ui.Button(label="内容を編集する", emoji="✍️", custom_id=f"edit_private_ticket", style=discord.ButtonStyle.green, row=1)
    button_2 = discord.ui.Button(label="確定する", disabled=False if data.get("report_button_channel") else True, emoji="👌", custom_id=f"settings_confirm_private_ticket", style=discord.ButtonStyle.red, row=1)
    button_3 = discord.ui.Button(label="パネルを設置しない", emoji="🗑️", custom_id=f"settings_delete_private_ticket", style=discord.ButtonStyle.gray, row=2)
    view.add_item(button_1)
    view.add_item(button_2)
    view.add_item(button_3)

    if error:
      await interaction.followup.edit_message(interaction.message.id, view=None)
      await interaction.followup.edit_message(interaction.message.id, embeds=embeds, view=view)
    else:
      await interaction.response.edit_message(embeds=embeds, view=view)


  async def settings_final(self, interaction:discord.Interaction):
    report_data = await self.get_data(interaction, type="report")
    pticket_data = await self.get_data(interaction, type="pticket")

    embed_2 = discord.Embed(
      description="## Report機能",
      color=0xF4BD44,
    )
    embed_2.add_field(
      name="Report送信チャンネル",
      value=interaction.guild.get_channel(report_data["report_send_channel"]).mention if report_data.get("report_send_channel") else "未設定",
      inline=True
    )
    embed_2.add_field(
      name="Report送信時メンションロール",
      value=interaction.guild.get_role(report_data["mention_role"]).mention if report_data.get("mention_role") else "未設定",
      inline=True
    )

    embed_3 = discord.Embed(
      description="## 匿名Ticket機能",
      color=0x9AC9FF,
    )
    embed_3.add_field(
      name="匿名Ticket送信チャンネル",
      value=interaction.guild.get_channel(pticket_data["report_send_channel"]).mention if pticket_data.get("report_send_channel") else "未設定",
      inline=True
    )
    if pticket_data.get("report_send_channel"):
      embed_3.add_field(
        name="匿名Ticket作成用ボタン送信チャンネル",
        value=interaction.guild.get_channel(pticket_data["report_button_channel"]).mention if pticket_data.get("report_button_channel") else "未設定",
        inline=True
      )
    embed_3.add_field(
      name="匿名Ticket送信時メンションロール",
      value=interaction.guild.get_role(pticket_data["mention_role"]).mention if pticket_data.get("mention_role") else "未設定",
      inline=True
    )

    await interaction.response.edit_message(embeds=[embed_2, embed_3] , view=None)

    # Report送信チャンネルが存在する場合
    if report_data.get("report_send_channel"):
      embed_2.set_author(
        name=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None,
      )
      # メンションロールを取得
      if report_data.get("mention_role"):
        mention_role_mention = interaction.guild.get_role(report_data["mention_role"]).mention
      else:
        mention_role_mention = None
      await interaction.guild.get_channel(report_data["report_send_channel"]).send(mention_role_mention, embed=embed_2)

    # Ticket送信チャンネルが存在 and Ticket作成用ボタンが存在する場合
    if pticket_data.get("report_send_channel"):
      embed_3.set_author(
        name=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None,
      )
      # メンションロールを取得
      if pticket_data.get("mention_role"):
        mention_role_mention = interaction.guild.get_role(pticket_data["mention_role"]).mention
      else:
        mention_role_mention = None

      await interaction.guild.get_channel(pticket_data["report_send_channel"]).send(mention_role_mention, embed=embed_3)


  @commands.Cog.listener()
  async def on_interaction(self, interaction):
    try:
      custom_id = interaction.data["custom_id"]
    except KeyError:
      return

    # settings_1
    if custom_id == "settings_page_1":
      embed, view = self.settings_page_1()
      await interaction.response.edit_message(embed=embed, view=view)

    # settings_2
    elif custom_id == "settings_page_2":
      await self.settings_page_2(interaction)

    # settings_3
    elif custom_id == "settings_page_3":
      await self.settings_page_3(interaction)

    # settings_panel_config
    elif custom_id == "settings_panel_config":
      await self.settings_panel_config(interaction)

    # Ticket作成用ボタンの場合
    elif custom_id == "settings_select_pticket_button_channel":
      channel, error_embed = self.check_permission(interaction, button_channel=True)
      if error_embed:
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        await self.settings_panel_config(interaction, error=True, value=interaction.message.embeds[1].description)
        return
      else:
        if channel:
          if not channel.permissions_for(interaction.user).manage_channels:
            embed=error.generate(
              code="1-5-05",
              description=f"あなたに{channel.mention}の`チャンネル管理`の権限が必要です。"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.settings_panel_config(interaction, error=True, value=interaction.message.embeds[1].description)
            return

        data = await self.get_data(interaction, type="pticket")
        data["report_button_channel"] = channel.id if channel else None
        await self.save_data(interaction, data, "pticket")
        await self.settings_panel_config(interaction, value=interaction.message.embeds[1].description)

    # チャンネル, ロールが選ばれた（選択解除された）場合
    elif "settings_select_" in custom_id:
      embed = interaction.message.embeds[0]

      # channelの場合 -> そのチャンネルのチャンネル管理権限があるか判定
      if "channel" in custom_id:
        if interaction.data["values"]:
          channel = interaction.guild.get_channel(int(interaction.data["values"][0]))
          if not channel.permissions_for(interaction.user).manage_channels:
            embed=error.generate(
              code="1-5-05",
              description=f"あなたに{channel.mention}の`チャンネル管理`の権限が必要です。"
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            if "report" in custom_id:
              await self.settings_page_2(interaction, error=True)
            else:
              await self.settings_page_3(interaction, error=True)

            return

      # Report設定の場合
      if "report" in custom_id:
        data = await self.get_data(interaction, type="report")

        # Report送信チャンネル設定の場合
        if custom_id == "settings_select_report_channel":
          channel, error_embed = self.check_permission(interaction)
          if error_embed:
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            await self.settings_page_2(interaction, error=True)
            return
          else:
            data["report_send_channel"] = channel.id if channel else None
        # Report送信時メンションロール設定の場合
        else:
          data["mention_role"] = int(interaction.data["values"][0]) if interaction.data["values"] else None

        await self.save_data(interaction, data, "report")
        await self.settings_page_2(interaction)

      # Ticket設定の場合
      else:
        data = await self.get_data(interaction, type="pticket")

        # Ticket送信チャンネル設定の場合
        if custom_id == "settings_select_pticket_channel":
          channel, error_embed = self.check_permission(interaction)
          if error_embed:
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            await self.settings_page_3(interaction, error=True)
            return
          else:
            data["report_send_channel"] = channel.id if channel else None
        # Ticket作成時メンションロールの場合
        elif custom_id == "settings_select_pticket_mention_role":
          data["mention_role"] = int(interaction.data["values"][0]) if interaction.data["values"] else None

        await self.save_data(interaction, data, "pticket")
        await self.settings_page_3(interaction)


    # 保存して終了ボタン
    elif custom_id == "settings_final":
      await self.settings_final(interaction)


    # 確定ボタンを押したとき
    elif interaction.data["custom_id"] == "settings_confirm_private_ticket":
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="匿名Ticket", emoji="🔖", custom_id=f"private_ticket", style=discord.ButtonStyle.primary, disabled=False, row=0)
      view.add_item(button_0)

      # フィールド, フッターを消す
      embed = interaction.message.embeds[1]
      embed.remove_field(0)
      embed.set_footer(text=None)

      # 送信する
      pticket_data = await self.get_data(interaction, type="pticket")
      msg = await interaction.guild.get_channel(pticket_data["report_button_channel"]).send(embed=embed, view=view)

      await self.settings_final(interaction)


    # 編集ボタンを押した場合
    elif interaction.data["custom_id"] == "edit_private_ticket":
      modal = EditPrivateModal(self.bot, interaction.message)
      await interaction.response.send_modal(modal)


    # パネル設置しないを押した場合
    elif interaction.data["custom_id"] == "settings_delete_private_ticket":
      await self.settings_final(interaction)


  # 閲覧権限確認
  def check_permission(self, interaction:discord.Interaction, button_channel:bool=False):
    if interaction.data["values"]:
      channel = interaction.guild.get_channel(int(interaction.data["values"][0]))

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

      # ボタン設置ちゃんねるのときは確認しない
      if not button_channel:
        if channel.permissions_for(bot_member).create_public_threads:
          permission_l.append(":white_check_mark:公開スレッドの作成")
        else:
          permission_l.append(":x:公開スレッドの作成")
          cannot = True

      if cannot:
        embed=error.generate(
          code="1-5-02",
          description=f"{channel.mention}にて、:x:の付いた権限が不足しています。チャンネル設定から権限を追加するか、別のチャンネルを選択してください。"
                      "\n\n- " + "\n- ".join(permission_l)
        )
        return channel, embed
      else:
        return channel, None

    else:
      return None, None


# パネル編集
class EditPrivateModal(discord.ui.Modal):
  def __init__(self, bot, msg):
    super().__init__(title=f'匿名Ticket開始パネル 編集モーダル')
    self.bot = bot
    self.msg = msg

    self.private_ticket_msg = discord.ui.TextInput(
      label="パネルに表示する内容を入力してください。",
      style=discord.TextStyle.long,
      default=msg.embeds[1].description,
      required=True,
      row=0
    )
    self.add_item(self.private_ticket_msg)

  async def on_submit(self, interaction: discord.Interaction):
    # 編集パネルの変更
    settings = Settings(self.bot)
    await settings.settings_panel_config(interaction, value=self.private_ticket_msg.value)



async def setup(bot):
  await bot.add_cog(Settings(bot))