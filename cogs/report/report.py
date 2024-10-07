from discord.ext import commands
from discord import app_commands
import discord

import os
import json
import aiofiles
import datetime

import error
import check



class Report(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.user_cooldowns = {}
    self.ctx_menu = app_commands.ContextMenu(
      name="!【サーバー管理者に報告】",
      callback=self.report,
    )
    self.bot.tree.add_command(self.ctx_menu)

  async def cog_unload(self):
    self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

  async def report(self, interaction:discord.Interaction, message:discord.Message):
    # jsonファイルがなかった場合 -> return
    path = f"data/report/guilds/{interaction.guild.id}.json"
    if not os.path.exists(path):
      embed=await error.generate(code="3-4-01")
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    # report送信チャンネルがなかった場合 -> return
    async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
      contents = await f.read()
    report_dict = json.loads(contents)

    if not report_dict.get("report_send_channel"):
      embed=await error.generate(code="3-4-02")
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    # guild_block
    embed = await check.is_guild_block(bot=self.bot, guild=interaction.guild, user_id=interaction.user.id)
    if embed:
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    # cooldown
    embed, self.user_cooldowns = check.user_cooldown(interaction.user.id, self.user_cooldowns)
    if embed:
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    button = ReportButton(self.bot, interaction, message)
    embed=discord.Embed(
      description="通常報告：報告者名がサーバー管理者に伝わる\n匿名報告：報告者名は誰にも伝わらない",
      color=0xF4BD44,
    )
    await interaction.response.send_message(embed=embed, view=button, ephemeral=True)



class ReportButton(discord.ui.View):
  def __init__(self, bot, interaction, message, timeout=30):
    super().__init__(timeout=timeout)
    self.bot = bot
    self.interaction = interaction
    self.message = message

    self.button_0 = discord.ui.Button(label='通常報告', custom_id='public_report', style=discord.ButtonStyle.primary)
    self.button_1 = discord.ui.Button(label='匿名報告', custom_id='private_report', style=discord.ButtonStyle.green)

    self.add_item(self.button_0)
    self.add_item(self.button_1)


  async def interaction_check(self, interaction: discord.Interaction):
    self.button_0.disabled = True
    self.button_1.disabled = True

    if interaction.data['custom_id'] == "public_report":
      await self.do_report(interaction, self.message, interaction.user)
    elif interaction.data['custom_id'] == "private_report":
      # DMにテストメッセージを送信する
      try:
        await interaction.user.send("テストメッセージ", silent=True, delete_after=0.1)
      except Exception:
        embed=await error.generate(code="3-4-03")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
      await self.do_report(interaction, self.message, None)


  async def do_report(self, interaction, message, reporter):
    # embedの定義
    embed=discord.Embed(
      title="報告",
      description=message.content,
      color=0xF4BD44,
    )
    embed.set_image(url=message.attachments[0].url if message.attachments else None)
    embed.set_author(
      name=f"投稿者：{message.author.display_name}",
      icon_url=message.author.display_avatar.url if message.author.display_avatar else None
    )
    embed.set_footer(
      text=reporter.display_name if reporter else "報告者：匿名",
      icon_url=reporter.display_avatar.url if reporter else None,
    )
    message.embeds.insert(0, embed)

    # report_send_channelの取得
    path = f"data/report/guilds/{interaction.guild.id}.json"
    async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
      contents = await f.read()
    report_dict = json.loads(contents)
    cha = interaction.guild.get_channel(report_dict["report_send_channel"])

    # chaが無かった場合->return
    if not cha:
      embed=await error.generate(code="3-4-04")
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    if "mention_role" in report_dict:
      mention_role_id = report_dict["mention_role"]
    else:
      mention_role_id = None

    # Ticketを送信
    if mention_role_id:
      msg = f"<@&{mention_role_id}>\n{self.bot.user.mention}"
    else:
      msg = self.bot.user.mention
    try:
      msg = await cha.send(f"{msg}\n参照元：{message.jump_url}", embeds=message.embeds)
    except Exception as e:
      e = f"\n[ERROR[3-4-05]]{datetime.datetime.now()}\n- GUILD_ID:{interaction.guild.id}\n{e}\n"
      print(e)
      embed=await error.generate(code="3-4-05")
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    # report理由記入modal
    modal = ReportReasonModal(reporter, msg, message)
    await interaction.response.send_modal(modal)


    # 匿名reportの場合 -> 報告者idを保存{msg.id: user.id}
    if not reporter:
      path = f"data/report/private_report/{interaction.guild.id}.json"
      if os.path.exists(path):
        async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
          contents = await f.read()
        private_dict = json.loads(contents)
      else:
        private_dict = {}

      private_dict[str(msg.id)] = interaction.user.id

      async with aiofiles.open(path, mode="w") as f:
        contents = json.dumps(private_dict, indent=2, ensure_ascii=False)
        await f.write(contents)

      # 返信ボタンを設置
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="報告に返信", custom_id=f"report_create_thread", style=discord.ButtonStyle.primary)
      view.add_item(button_0)

      await msg.edit(view=view)


    await interaction.followup.edit_message(interaction.message.id, view=self)


class ReportReasonModal(discord.ui.Modal):
  def __init__(self, reporter, msg, reported_msg):
    super().__init__(title=f'報告理由記入用modal')
    self.reporter = reporter
    self.msg = msg
    self.reported_msg = reported_msg

    self.report_reason = discord.ui.TextInput(
      label="報告の理由(不快に思った点など)を記入してください",
      style=discord.TextStyle.long,
      required=True,
      row=0
    )
    self.add_item(self.report_reason)

  async def on_submit(self, interaction: discord.Interaction):
    embed=discord.Embed(
      title="報告の理由",
      description=self.report_reason.value,
      color=0xF4BD44,
    )
    embed.set_footer(
      text=self.reporter.display_name if self.reporter else "報告者：匿名",
      icon_url=self.reporter.display_avatar.url if self.reporter else None,
    )
    embeds = self.msg.embeds or []
    embeds.append(embed)
    await self.msg.edit(embeds=embeds)

    if self.reporter:
      await interaction.response.send_message("報告が完了しました。\nありがとうございました。\n\nサーバー管理者から直接話を伺うことがあります。", ephemeral=True)
    else:
      await interaction.response.send_message("送信されました。\nこのbotのDMをご確認ください。", ephemeral=True)

      # 匿名Report完了確認membedを定義

      embed_1=discord.Embed(
        url=self.msg.jump_url,
        description=f"## 匿名Report\n### Reportしたメッセージ\n　{self.reported_msg.jump_url}\n### Report内容\n{self.report_reason.value}",
        color=0xF4BD44,
      )
      embed_1.set_footer(
          text=f"匿名Report | {interaction.guild.name}",
          icon_url=interaction.guild.icon.replace(format='png').url if interaction.guild.icon else None,
        )

      embed_2=discord.Embed(
        description="- ファイルを添付する場合や追加で何か送信する場合は、**このメッセージに返信**する形で送信してください。\n"
                    "- あなたの情報(ユーザー名, idなど)が外部に漏れることは一切ありません。",
        color=0xF4BD44,
      )
      await interaction.user.send(embeds=[embed_1, embed_2])



async def setup(bot):
  await bot.add_cog(Report(bot))