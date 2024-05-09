from discord.ext import commands
from discord import app_commands
import discord
import os
import json



class Reply(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_interaction(self, interaction:discord.Interaction):
    try:
      custom_id = interaction.data["custom_id"]
    except KeyError:
      return

    # privateのやつがなかった場合 -> return
    if custom_id in ["report_reply", "report_edit_reply", "report_send"]:
      path = f"data/report/private_report/{interaction.guild.id}.json"
      if not os.path.exists(path):
        await interaction.response.send_message("guildファイルが存在しません。サポートサーバーに問い合わせてください。", ephemeral=True)
        return

    if custom_id == "report_reply":
      # thread作成, 送信
      thread = await interaction.message.create_thread(name="匿名報告への返信")

      view = discord.ui.View()
      button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"report_edit_reply", style=discord.ButtonStyle.primary)
      button_1 = discord.ui.Button(label="送信する", custom_id=f"report_send", style=discord.ButtonStyle.red)
      view.add_item(button_0)
      view.add_item(button_1)
      await thread.send("【返信内容】\n下のボタンから編集してください。", view=view)

      await interaction.response.send_message("こちらのスレッドから返信を行えます。", ephemeral=True)


    # スレッド内での返信編集
    elif custom_id == "report_edit_reply":
      modal = EditReplyModal(interaction.message)
      await interaction.response.send_modal(modal)


    elif custom_id == "report_send":
      with open(path, encoding='utf-8', mode="r") as f:
        private_dict = json.load(f)

      # 報告者に返信
      reporter_id = private_dict[str(interaction.channel.id)]
      reporter = await interaction.guild.fetch_member(reporter_id)
      embed = discord.Embed(
        url = interaction.channel.jump_url,
        description=f"あなたの報告に関して、 {interaction.guild.name} の管理者から返信が届きました。\n"
                    "### ------------返信内容------------\n"
                    f"{interaction.message.content.replace('【返信内容】','')}\n"
                    "### --------------------------------\n"
                    "- あなたの情報(ユーザー名, idなど)が外部に漏れることは一切ありません。\n"
                    f"- __**このメッセージに返信**__(右クリック→返信)すると、{interaction.guild.name}の管理者に届きます。",
      )
      try:
        await reporter.send(embed=embed)
        # view削除
        await interaction.message.edit(view=None)
        await interaction.message.add_reaction("✅")

      except discord.error.Forbidden:
        await interaction.response.send_message("報告者がDMを受け付けてないため、送信されませんでした。")
      except Exception as e:
        await interaction.response.send_message("不明なエラーが発生しました。サポートサーバーに問い合わせてください。")
        print(f"[ERROR]\n{e}")


    elif custom_id == "report_cancel":
      await interaction.message.delete()


class EditReplyModal(discord.ui.Modal):
  def __init__(self, msg):
    super().__init__(title=f'報告への返信用modal')
    self.msg = msg

    # modalのdefaultを定義
    if "下のボタンから編集してください。" in self.msg.content:
      default = None
    else:
      default = self.msg.content.replace("【返信内容】\n","")

    self.reply = discord.ui.TextInput(
      label="返信内容を入力（送信ボタンで一時保存できます。）",
      style=discord.TextStyle.long,
      default=default,
      required=True,
      row=0
    )
    self.add_item(self.reply)

  async def on_submit(self, interaction: discord.Interaction):
    await self.msg.edit(content = f"【返信内容】\n{self.reply.value}")
    await interaction.response.defer(thinking=True)
    m = await interaction.followup.send("\u200b")
    await m.delete()


async def setup(bot):
  await bot.add_cog(Reply(bot))