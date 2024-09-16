from discord.ext import commands
from discord import app_commands
import discord

import aiofiles
import json
import os

import cog_list



dev_cog_list = cog_list.dev_cog_list

class Quickstart(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="quickstart", description='簡単設定')
  async def quickstart(self, interaction:discord.Interaction):
    if not interaction.channel.permissions_for(interaction.user).manage_channels:
      return await interaction.response.send_message("権限不足", ephemeral=True)
    embed, view = self.quickstart_page_1()
    await interaction.response.send_message(self.bot.user.mention, embed=embed, view=view, ephemeral=True)


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


  def quickstart_page_1(self):
    embed = discord.Embed(
      title="Quickstart (1/3)",
      description="全ての設定を行います。",
      color=0xF4BD44,
    )
    view = discord.ui.View()
    button = discord.ui.Button(label="次へ", emoji="➡️", custom_id=f"quickstart_page_2", style=discord.ButtonStyle.green, row=0)
    view.add_item(button)
    return embed, view


  @commands.Cog.listener()
  async def on_interaction(self, interaction):
    try:
      custom_id = interaction.data["custom_id"]
    except KeyError:
      return


    if custom_id == "quickstart_page_1":
      embed, view = self.quickstart_page_1()
      await interaction.response.edit_message(embed=embed, view=view)


    elif custom_id == "quickstart_page_2":
      data = await self.get_data(interaction, type="report")
      embed = discord.Embed(
        title="Quickstart (2/3)",
        description="## Report機能の設定",
        color=0xF4BD44,
      )
      embed.add_field(
        name="Report送信チャンネル（必須）",
        value=interaction.guild.get_channel(data["report_send_channel"]).mention if "report_send_channel" in data and data["report_send_channel"] else None,
        inline=True
      )
      embed.add_field(
        name="Report送信時メンションロール（任意）",
        value=interaction.guild.get_role(data["mention_role"]).mention if "mention_role" in data and data["mention_role"] else None,
        inline=True
      )

      view = discord.ui.View()
      select_0 = discord.ui.ChannelSelect(
        custom_id="quickstart_select_report_channel",
        channel_types=[discord.ChannelType.text],
        placeholder="Report送信チャンネル（必須）",
        min_values=0,
        default_values=[interaction.guild.get_channel(data["report_send_channel"])] if "report_send_channel" in data and data["report_send_channel"] else None,
        row=0
      )
      select_1 = discord.ui.RoleSelect(
        custom_id="quickstart_select_report_mention_role",
        placeholder="Report送信時メンションロール（任意）",
        min_values=0,
        default_values=[interaction.guild.get_role(data["mention_role"])] if "mention_role" in data and data["mention_role"] else None,
        row=1
      )
      view.add_item(select_0)
      view.add_item(select_1)

      button_0 = discord.ui.Button(label="戻る", custom_id=f"quickstart_page_1", style=discord.ButtonStyle.gray, row=2)
      button_1 = discord.ui.Button(label="リロード", custom_id=f"quickstart_page_2", style=discord.ButtonStyle.green, row=2)
      button_2 = discord.ui.Button(label="保存して次へ", custom_id=f"quickstart_page_3", style=discord.ButtonStyle.primary, row=2)
      view.add_item(button_0)
      view.add_item(button_1)
      view.add_item(button_2)
      await interaction.response.edit_message(embed=embed, view=view)


    elif custom_id == "quickstart_page_3":
      data = await self.get_data(interaction, type="pticket")
      embed = discord.Embed(
        title="Quickstart (2/3)",
        description="## 匿名Ticket機能の設定",
        color=0xF4BD44,
      )
      embed.add_field(
        name="匿名Ticket送信チャンネル（必須）",
        value=interaction.guild.get_channel(data["report_send_channel"]).mention if "report_send_channel" in data and data["report_send_channel"] else None,
        inline=True
      )
      embed.add_field(
        name="匿名Ticket作成用ボタン送信チャンネル（必須）",
        value=interaction.guild.get_channel(data["report_button_channel"]).mention if "report_button_channel" in data and data["report_button_channel"] else None,
        inline=True
      )
      embed.add_field(
        name="匿名Ticket送信時メンションロール（任意）",
        value=interaction.guild.get_role(data["mention_role"]).mention if "mention_role" in data and data["mention_role"] else None,
        inline=True
      )

      view = discord.ui.View()
      select_0 = discord.ui.ChannelSelect(
        custom_id="quickstart_select_pticket_channel",
        channel_types=[discord.ChannelType.text],
        placeholder="匿名Ticket送信チャンネル（必須）",
        min_values=0,
        default_values=[interaction.guild.get_channel(data["report_send_channel"])] if "report_send_channel" in data and data["report_send_channel"] else None,
        row=0
      )
      select_1 = discord.ui.ChannelSelect(
        custom_id="quickstart_select_pticket_button_channel",
        channel_types=[discord.ChannelType.text],
        placeholder="匿名Ticket作成用ボタン送信チャンネル（必須）",
        min_values=0,
        default_values=[interaction.guild.get_channel(data["report_button_channel"])] if "report_button_channel" in data and data["report_button_channel"] else None,
        row=1
      )
      select_2 = discord.ui.RoleSelect(
        custom_id="quickstart_select_pticket_mention_role",
        placeholder="匿名Ticket送信時メンションロール（任意）",
        min_values=0,
        default_values=[interaction.guild.get_role(data["mention_role"])] if "mention_role" in data and data["mention_role"] else None,
        row=2
      )
      view.add_item(select_0)
      view.add_item(select_1)
      view.add_item(select_2)
      button_0 = discord.ui.Button(label="戻る", custom_id=f"quickstart_page_2", style=discord.ButtonStyle.gray, row=3)
      button_1 = discord.ui.Button(label="リロード", custom_id=f"quickstart_page_3", style=discord.ButtonStyle.green, row=3)
      button_2 = discord.ui.Button(label="保存して終了", custom_id=f"quickstart_final", style=discord.ButtonStyle.primary, row=3)
      view.add_item(button_0)
      view.add_item(button_1)
      view.add_item(button_2)
      await interaction.response.edit_message(embed=embed, view=view)


    elif "quickstart_select_" in custom_id:
      embed = interaction.message.embeds[0]

      if "report" in custom_id:
        data = await self.get_data(interaction, type="report")

        if custom_id == "quickstart_select_report_channel":
          embed.set_field_at(
            index=0,
            name="Report送信チャンネル（必須）",
            value=interaction.guild.get_channel(int(interaction.data["values"][0])).mention if interaction.data["values"] else "未設定"
          )
          data["report_send_channel"] = int(interaction.data["values"][0]) if interaction.data["values"] else None
        else:
          embed.set_field_at(
            index=1,
            name="Report送信時メンションロール（任意）",
            value=interaction.guild.get_role(int(interaction.data["values"][0])).mention if interaction.data["values"] else "未設定"
          )
          data["mention_role"] = int(interaction.data["values"][0]) if interaction.data["values"] else None

        await self.save_data(interaction, data, "report")


      else:
        data = await self.get_data(interaction, type="pticket")

        if custom_id == "quickstart_select_pticket_channel":
          embed.set_field_at(
            index=0,
            name="匿名Ticket送信チャンネル（必須）",
            value=interaction.guild.get_channel(int(interaction.data["values"][0])).mention if interaction.data["values"] else "未設定"
          )
          data["report_send_channel"] = int(interaction.data["values"][0]) if interaction.data["values"] else None
        elif custom_id == "quickstart_select_pticket_button_channel":
          embed.set_field_at(
            index=1,
            name="匿名Ticket作成用ボタン送信チャンネル（必須）",
            value=interaction.guild.get_channel(int(interaction.data["values"][0])).mention if interaction.data["values"] else "未設定"
          )
          data["report_button_channel"] = int(interaction.data["values"][0]) if interaction.data["values"] else None
        else:
          embed.set_field_at(
            index=2,
            name="匿名Ticket送信時メンションロール（任意）",
            value=interaction.guild.get_role(int(interaction.data["values"][0])).mention if interaction.data["values"] else "未設定"
          )
          data["mention_role"] = int(interaction.data["values"][0]) if interaction.data["values"] else None

        await self.save_data(interaction, data, "pticket")

      await interaction.response.edit_message(embed=embed)


    elif custom_id == "quickstart_final":
      report_data = await self.get_data(interaction, type="report")
      pticket_data = await self.get_data(interaction, type="pticket")

      embed_1 = discord.Embed(
        title="Quickstart",
        description="設定が完了しました。",
        color=0xF4BD44,
      )

      embed_2 = discord.Embed(
        description="## Report機能の設定",
        color=0xF4BD44,
      )
      embed_2.add_field(
        name="Report送信チャンネル（必須）",
        value=interaction.guild.get_channel(report_data["report_send_channel"]).mention if "report_send_channel" in report_data and report_data["report_send_channel"] else None,
        inline=True
      )
      embed_2.add_field(
        name="Report送信時メンションロール（任意）",
        value=interaction.guild.get_role(report_data["mention_role"]).mention if "mention_role" in report_data and report_data["mention_role"] else None,
        inline=True
      )

      embed_3 = discord.Embed(
        description="## 匿名Ticket機能の設定",
        color=0xF4BD44,
      )
      embed_3.add_field(
        name="匿名Ticket送信チャンネル（必須）",
        value=interaction.guild.get_channel(pticket_data["report_send_channel"]).mention if "report_send_channel" in pticket_data and pticket_data["report_send_channel"] else None,
        inline=True
      )
      embed_3.add_field(
        name="匿名Ticket作成用ボタン送信チャンネル（必須）",
        value=interaction.guild.get_channel(pticket_data["report_button_channel"]).mention if "report_button_channel" in pticket_data and pticket_data["report_button_channel"] else None,
        inline=True
      )
      embed_3.add_field(
        name="匿名Ticket送信時メンションロール（任意）",
        value=interaction.guild.get_role(pticket_data["mention_role"]).mention if "mention_role" in pticket_data and pticket_data["mention_role"] else None,
        inline=True
      )

      await interaction.response.edit_message(embeds=[embed_1, embed_2, embed_3] , view=None)

      embed_2.set_author(
        name=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
      )
      await interaction.guild.get_channel(report_data["report_send_channel"]).send(embed=embed_2)

      embed_3.set_author(
        name=f"実行者:{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
      )
      await interaction.guild.get_channel(pticket_data["report_send_channel"]).send(embed=embed_3)

      embed=discord.Embed(
        title="匿名Ticket",
        description="匿名Ticketを作成します。\nこのbotのDMを通じて匿名でサーバー管理者と会話することができます。",
        color=0x9AC9FF,
      )
      embed.set_footer(
        text="＊下のボタンから匿名Ticket開始パネルのメッセージを編集することができます。"
      )
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="匿名Ticket", emoji="🔖", custom_id=f"private_ticket", style=discord.ButtonStyle.primary, disabled=True, row=0)
      button_1 = discord.ui.Button(label="内容を編集する", emoji="✍️", custom_id=f"edit_private_ticket", style=discord.ButtonStyle.green, row=1)
      button_2 = discord.ui.Button(label="確定する", emoji="👌", custom_id=f"quickstart_confirm_private_ticket", style=discord.ButtonStyle.red, row=1)
      view.add_item(button_0)
      view.add_item(button_1)
      view.add_item(button_2)
      await interaction.followup.send(embed=embed, view=view)


        # 確定ボタンを押したとき
    elif interaction.data["custom_id"] == "quickstart_confirm_private_ticket":
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="匿名Ticket", emoji="🔖", custom_id=f"private_ticket", style=discord.ButtonStyle.primary, disabled=False, row=0)
      view.add_item(button_0)
      await interaction.response.edit_message(content="ok", embed=None, view=None)

      # フッターを消す
      embed = interaction.message.embeds[0]
      embed.set_footer(text=None)

      # 送信する
      pticket_data = await self.get_data(interaction, type="pticket")
      await interaction.guild.get_channel(pticket_data["report_button_channel"]).send(embed=embed, view=view)



async def setup(bot):
  await bot.add_cog(Quickstart(bot))