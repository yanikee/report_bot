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

  @app_commands.command(name="settings", description='簡単設定')
  async def settings(self, interaction:discord.Interaction):
    if not interaction.channel.permissions_for(interaction.user).manage_channels:
      embed = error.generate(
        code="1-5-01",
        description=f"権限不足です。\n`チャンネル管理`の権限が必要です。",
      )
      return await interaction.response.send_message(embed=embed, ephemeral=True)

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


  async def settings_page_2(self, interaction:discord.Interaction):
    data = await self.get_data(interaction, type="report")

    # Embedの定義
    embed = discord.Embed(
      title="settings (2/3)",
      description="## Report機能の設定\n以下の**2つ**の設定を行ってください\n(Report機能を無効化したい場合は、全ての項目を未選択にしてください)",
      color=0xF4BD44,
    )
    embed.add_field(
      name=("🔵" if "report_send_channel" in data and data["report_send_channel"] else "⚪") + "Report送信チャンネル",
      value="\n- Reportを送信するチャンネルを設定します\n",
      inline=False
    )
    embed.add_field(
      name=("🔵" if "mention_role" in data and data["mention_role"] else "⚪") + "Report送信時メンションロール(任意)",
      value="- Reportが送信されたときにメンションするロールを設定します",
      inline=False
    )

    view = discord.ui.View()
    select_0 = discord.ui.ChannelSelect(
      custom_id="settings_select_report_channel",
      channel_types=[discord.ChannelType.text],
      placeholder="Report送信チャンネル(未選択)",
      min_values=0,
      default_values=[interaction.guild.get_channel(data["report_send_channel"])] if "report_send_channel" in data and data["report_send_channel"] else None,
      row=0
    )
    select_1 = discord.ui.RoleSelect(
      custom_id="settings_select_report_mention_role",
      placeholder="Report送信時メンションロール(未選択)",
      min_values=0,
      default_values=[interaction.guild.get_role(data["mention_role"])] if "mention_role" in data and data["mention_role"] else None,
      row=1
    )
    view.add_item(select_0)
    view.add_item(select_1)

    button_0 = discord.ui.Button(label="戻る", custom_id=f"settings_page_1", style=discord.ButtonStyle.gray, row=2)
    button_1 = discord.ui.Button(label="次へ", custom_id=f"settings_page_3", style=discord.ButtonStyle.primary, row=2)
    view.add_item(button_0)
    view.add_item(button_1)

    await interaction.response.edit_message(embed=embed, view=view)


  async def settings_page_3(self, interaction:discord.Interaction):
    data = await self.get_data(interaction,type="pticket")
    embed = discord.Embed(
      title="settings (3/3)",
      description="## 匿名Ticket機能の設定\n以下の**3つ**の設定を行ってください\n(匿名Ticket機能を無効化したい場合は、全ての項目を未選択にしてください)",
      color=0x9AC9FF,
    )
    embed.add_field(
      name=("🔵" if "report_send_channel" in data and data["report_send_channel"] else "⚪") + "匿名Ticket送信チャンネル",
      value="- 匿名Ticketを送信するチャンネルを設定します",
      inline=False
    )
    embed.add_field(
      name=("🔵" if "report_button_channel" in data and data["report_button_channel"] else "⚪") + "匿名Ticket作成用ボタン送信チャンネル",
      value="- 匿名Ticketを作成するためのボタンを送信するチャンネルを設定します",
      inline=False
    )
    embed.add_field(
      name=("🔵" if "mention_role" in data and data["mention_role"] else "⚪") + "匿名Ticket送信時メンションロール(任意)",
      value="- 匿名Ticketが送信されたときにメンションするロールを設定します",
      inline=False
    )

    view = discord.ui.View()
    select_0 = discord.ui.ChannelSelect(
      custom_id="settings_select_pticket_channel",
      channel_types=[discord.ChannelType.text],
      placeholder="匿名Ticket送信チャンネル(未選択)",
      min_values=0,
      default_values=[interaction.guild.get_channel(data["report_send_channel"])] if "report_send_channel" in data and data["report_send_channel"] else None,
      row=0
    )
    select_1 = discord.ui.ChannelSelect(
      custom_id="settings_select_pticket_button_channel",
      channel_types=[discord.ChannelType.text],
      placeholder="匿名Ticket作成用ボタン送信チャンネル(未選択)",
      min_values=0,
      default_values=[interaction.guild.get_channel(data["report_button_channel"])] if "report_button_channel" in data and data["report_button_channel"] else None,
      row=1
    )
    select_2 = discord.ui.RoleSelect(
      custom_id="settings_select_pticket_mention_role",
      placeholder="匿名Ticket送信時メンションロール(未選択)",
      min_values=0,
      default_values=[interaction.guild.get_role(data["mention_role"])] if "mention_role" in data and data["mention_role"] else None,
      row=2
    )
    view.add_item(select_0)
    view.add_item(select_1)
    view.add_item(select_2)

    button_0 = discord.ui.Button(label="戻る", custom_id=f"settings_page_2", style=discord.ButtonStyle.gray, row=3)
    button_1 = discord.ui.Button(label="保存して終了", custom_id=f"settings_final", style=discord.ButtonStyle.red, row=3)
    view.add_item(button_0)
    view.add_item(button_1)

    await interaction.response.edit_message(embed=embed, view=view)


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
            return

      # Report設定の場合
      if "report" in custom_id:
        data = await self.get_data(interaction, type="report")

        # Report送信チャンネル設定の場合
        if custom_id == "settings_select_report_channel":
          channel, error_embed = self.check_permission(interaction)
          if error_embed:
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
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
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
          data["report_send_channel"] = channel.id if channel else None
        # Ticket作成用ボタンの場合
        elif custom_id == "settings_select_pticket_button_channel":
          channel, error_embed = self.check_permission(interaction, button_channel=True)
          if error_embed:
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
          data["report_button_channel"] = channel.id if channel else None
        # Ticket作成時メンションロールの場合
        else:
          data["mention_role"] = int(interaction.data["values"][0]) if interaction.data["values"] else None

        await self.save_data(interaction, data, "pticket")
        await self.settings_page_3(interaction)


    # 保存して終了ボタン
    elif custom_id == "settings_final":
      report_data = await self.get_data(interaction, type="report")
      pticket_data = await self.get_data(interaction, type="pticket")

      # report_send_channelしか選択してなかった場合
      if (pticket_data["report_send_channel"] and not pticket_data["report_button_channel"]) or (pticket_data["report_send_channel"] and not "report_button_channel" in pticket_data):
        embed = error.generate(
          code="1-5-03",
          description=f"片方のチャンネルのみを設定することはできません。\n**匿名Ticket作成用ボタン送信チャンネル**の設定が必要です",
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
      # report_button_channelしか選択してなかった場合
      elif (pticket_data["report_button_channel"] and not pticket_data["report_send_channel"]) or (pticket_data["report_button_channel"] and not "report_send_channel" in pticket_data):
        embed = error.generate(
          code="1-5-04",
          description=f"片方のチャンネルのみを設定することはできません。\n**匿名Ticket送信チャンネル**の設定が必要です",
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

      embed_1 = discord.Embed(
        title="settings",
        description="設定が完了しました。",
        color=0xF4BD44,
      )

      embed_2 = discord.Embed(
        description="## Report機能",
        color=0xF4BD44,
      )
      embed_2.add_field(
        name="Report送信チャンネル",
        value=interaction.guild.get_channel(report_data["report_send_channel"]).mention if "report_send_channel" in report_data and report_data["report_send_channel"] else "未設定",
        inline=True
      )
      embed_2.add_field(
        name="Report送信時メンションロール",
        value=interaction.guild.get_role(report_data["mention_role"]).mention if "mention_role" in report_data and report_data["mention_role"] else "未設定",
        inline=True
      )

      embed_3 = discord.Embed(
        description="## 匿名Ticket機能",
        color=0x9AC9FF,
      )
      embed_3.add_field(
        name="匿名Ticket送信チャンネル",
        value=interaction.guild.get_channel(pticket_data["report_send_channel"]).mention if "report_send_channel" in pticket_data and pticket_data["report_send_channel"] else "未設定",
        inline=True
      )
      embed_3.add_field(
        name="匿名Ticket作成用ボタン送信チャンネル",
        value=interaction.guild.get_channel(pticket_data["report_button_channel"]).mention if "report_button_channel" in pticket_data and pticket_data["report_button_channel"] else "未設定",
        inline=True
      )
      embed_3.add_field(
        name="匿名Ticket送信時メンションロール",
        value=interaction.guild.get_role(pticket_data["mention_role"]).mention if "mention_role" in pticket_data and pticket_data["mention_role"] else "未設定",
        inline=True
      )

      await interaction.response.edit_message(embeds=[embed_1, embed_2, embed_3] , view=None)


      # Report送信チャンネルが存在する場合
      if report_data["report_send_channel"]:
        embed_2.set_author(
          name=f"実行者:{interaction.user.display_name}",
          icon_url=interaction.user.display_avatar.url,
        )
        # メンションロールを取得
        mention_role_mention = None
        if "mention_role" in report_data:
          if report_data["mention_role"]:
            mention_role_mention = interaction.guild.get_role(report_data["mention_role"]).mention
        await interaction.guild.get_channel(report_data["report_send_channel"]).send(mention_role_mention, embed=embed_2)

      # Ticket送信チャンネルが存在 and Ticket作成用ボタンが存在する場合
      if pticket_data["report_send_channel"] and pticket_data["report_button_channel"]:
        embed_3.set_author(
          name=f"実行者:{interaction.user.display_name}",
          icon_url=interaction.user.display_avatar.url,
        )
        # メンションロールを取得
        mention_role_mention = None
        if "mention_role" in pticket_data:
          if pticket_data["mention_role"]:
            mention_role_mention = interaction.guild.get_role(pticket_data["mention_role"]).mention

        await interaction.guild.get_channel(pticket_data["report_send_channel"]).send(mention_role_mention, embed=embed_3)

        embed = discord.Embed(
          title="匿名Ticket",
          description="匿名Ticketを作成します。\nこのbotのDMを通じて匿名でサーバー管理者と会話することができます。",
          color=0x9AC9FF,
        )
        embed.set_footer(
          text="・下のボタンから匿名Ticket開始パネルのメッセージを編集することができます。\n"
                "・パネルを作成する必要がない場合は、無視して構いません。",
        )
        view = discord.ui.View()
        button_1 = discord.ui.Button(label="内容を編集する", emoji="✍️", custom_id=f"edit_private_ticket", style=discord.ButtonStyle.green, row=1)
        button_2 = discord.ui.Button(label="確定する", emoji="👌", custom_id=f"settings_confirm_private_ticket", style=discord.ButtonStyle.red, row=1)
        view.add_item(button_1)
        view.add_item(button_2)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


    # 確定ボタンを押したとき
    elif interaction.data["custom_id"] == "settings_confirm_private_ticket":
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="匿名Ticket", emoji="🔖", custom_id=f"private_ticket", style=discord.ButtonStyle.primary, disabled=False, row=0)
      view.add_item(button_0)

      # フッターを消す
      embed = interaction.message.embeds[0]
      embed.set_footer(text=None)

      # 送信する
      pticket_data = await self.get_data(interaction, type="pticket")
      msg = await interaction.guild.get_channel(pticket_data["report_button_channel"]).send(embed=embed, view=view)

      # 確認msg送信
      embed = discord.Embed(
        description=f"Ticket作成用ボタンを設置しました。\n{msg.jump_url}",
        color=0x9AC9FF,
      )
      await interaction.response.edit_message(embed=embed, view=None)


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
          description=f"{channel.mention}にて、:x:の付いた権限が不足しています。チャンネル設定から権限を追加するか、別のチャンネルを選択してください。\n"
                      "全て:x:の場合、**チャンネル権限にreport bot!のロールを追加し、「メッセージを見る」を付与**すれば、解決することが多いです。"
                      "\n\n- " + "\n- ".join(permission_l)
        )
        return channel, embed
      else:
        return channel, None

    else:
      return None, None



async def setup(bot):
  await bot.add_cog(Settings(bot))
