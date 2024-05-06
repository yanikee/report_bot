from discord.ext import commands
from discord import app_commands
import discord
import os
import json



class Report(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.ctx_menu = app_commands.ContextMenu(
      name="!【運営に報告】",
      callback=self.report,
    )
    self.bot.tree.add_command(self.ctx_menu)

  async def cog_unload(self):
    self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

  async def report(self, interaction:discord.Interaction, message:discord.Message):
    # jsonファイルがなかった場合 -> return
    path = f"data/report/guilds/{interaction.guild.id}.json"
    if not os.path.exists(path):
      await interaction.response.send_message("サーバーの運営の方に、configコマンドを実行してもらってください。", ephemeral=True)
      return

    # report送信チャンネルがなかった場合 -> return
    with open(path, encoding='utf-8', mode="r") as f:
      report_dict = json.load(f)
    if not "report_send_channel" in report_dict:
      await interaction.response.send_message("サーバーの運営の方に、configコマンドを実行してもらってください。", ephemeral=True)
      return

    button = ReportButton(interaction, message)
    embed=discord.Embed(
      description="通常報告：報告者名が運営に伝わる\n匿名報告：報告者名は誰にも伝わらない",
      color=0x51FF91,
    )
    await interaction.response.send_message(embed=embed, view=button, ephemeral=True)



class ReportButton(discord.ui.View):
  def __init__(self, interaction, message, timeout=30):
    super().__init__(timeout=timeout)
    self.interaction = interaction
    self.message = message

    button_0 = discord.ui.Button(label='通常報告', custom_id='public_report', style=discord.ButtonStyle.primary)
    button_1 = discord.ui.Button(label='匿名報告', custom_id='private_report', style=discord.ButtonStyle.green)

    self.add_item(button_0)
    self.add_item(button_1)

  async def interaction_check(self, interaction: discord.Interaction):
    if interaction.data['custom_id'] == "public_report":
      await self.do_report(interaction, self.message, interaction.user)
    elif interaction.data['custom_id'] == "private_report":
      await self.do_report(interaction, self.message, None)


  async def do_report(self, interaction, message, reporter):
    # embedの定義
    embed=discord.Embed(
      title="報告",
      description=message.content
    )
    embed.set_image(url=message.attachments[0].url if message.attachments else None)
    embed.set_author(
      name=f"投稿者：{message.author.display_name}",
      icon_url=message.author.display_avatar.url
    )
    embed.set_footer(
      text=reporter.display_name if reporter else "報告者：匿名",
      icon_url=reporter.display_avatar.url if reporter else None,
    )
    message.embeds.insert(0, embed)

    # report_send_channelの取得
    path = f"data/report/guilds/{interaction.guild.id}.json"
    with open(path, encoding='utf-8', mode="r") as f:
      report_dict = json.load(f)
    cha = interaction.guild.get_channel(report_dict["report_send_channel"])

    msg = await cha.send(f"<@{1237001692977827920}>\n{message.jump_url}", embeds=message.embeds)

    # 返信ボタンを設置
    view = discord.ui.View()
    button_0 = discord.ui.Button(label="報告に返信", custom_id=f"report_reply", style=discord.ButtonStyle.primary)
    view.add_item(button_0)

    await msg.edit(view=view)


    # 匿名reportの場合 -> 報告者idを保存
    if not reporter:
      path = f"data/report/private_report/{interaction.guild.id}.json"
      if os.path.exists(path):
        with open(path, encoding='utf-8', mode="r") as f:
          private_dict = json.load(f)
      else:
        private_dict = {}

      private_dict[str(msg.id)] = interaction.user.id

      with open(path, mode="w") as f:
        json.dump(private_dict, f, indent=2, ensure_ascii=False)


    # report理由記入modal
    modal = ReportReasonModal(reporter, msg)
    await interaction.response.send_modal(modal)


class ReportReasonModal(discord.ui.Modal):
  def __init__(self, reporter, msg):
    super().__init__(title=f'報告理由記入用modal')
    self.reporter = reporter
    self.msg = msg

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
    )
    embed.set_footer(
      text=self.reporter.display_name if self.reporter else "報告者：匿名",
      icon_url=self.reporter.display_avatar.url if self.reporter else None,
    )
    embeds = self.msg.embeds or []
    embeds.append(embed)
    await self.msg.edit(embeds=embeds)

    await interaction.response.send_message("報告が完了しました。\nありがとうございました。", ephemeral=True)
    return


async def setup(bot):
  await bot.add_cog(Report(bot))