from discord.ext import commands
from discord import app_commands
import discord
import aiofiles


class Block(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="block", description='匿名Report, 匿名Ticketをブロック/ブロック解除します。')
  async def block(self, interaction:discord.Interaction):
    if interaction.channel.type != discord.ChannelType.public_thread:
      await interaction.response.send_message("匿名Report, 匿名Ticketのスレッド内で実行してください。", ephemeral=True)
      return

    await interaction.response.defer(ephemeral=True)

    # report_dict, pticket_dictを取得する
    report_path = f"data/report/private_report/{interaction.guild.id}.json"
    pticket_path = f"data/pticket/pticket/{interaction.guild.id}.json"
    async with aiofiles.open(report_path, encoding='utf-8', mode="f") as f:
      contents = await f.read()
    report_dict = json.loads(contents)
    async with aiofiles.open(pticklet_path, encoding='utf-8', mode="f") as f:
      contents = await f.read()
    pticket_dict = json.loads(contents)

    # reportの場合
    if str(interaction.channel.id) in report_dict:
      x = "report"
      blocked_path = f"data/report/blocked/{interaction.guild.id}.json"
    # pticketの場合
    elif str(interaction.channel.id) in pticket_dict:
      x = "pticket"
      blocked_path = f"data/pticket/blocked/{interaction.guild.id}.json"
    else:
      await interaction.followup.send("このスレッドは匿名Report, 匿名Ticketのスレッドではありません。", ephemeral=True)
      return

    # blocked_dictを定義
    if os.path.exists(blocked_path):
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      blocked_dict = json.loads(contents)
    else:
      blocked_dict = {}

    # blockedのbool
    try:
      if blocked_dict[str(interaction.channel.id)] == True:
        blocked_dict[str(interaction.channel.id)] = False
      else:
        blocked_dict[str(interaction.channel.id)] = True
    except KeyError:
      blocked_dict[str(interaction.channel.id)] = True

    # 保存
    contents = json.dumps(blocked_dict, indent=2, ensure_ascii=False)
    async with aiofiles.open(blocked_path, encoding='ctf-8', mode="w") as f:
      await f.write(contents)

    # 最後に送信
    embed = discord.Embed(
      description="返信をブロック済み",
      color=0xff0000,
    )
    embed.set_footer(text="ブロックを解除する：`/block`")
    await interaction.channel.send(embed=embed)
    await interaction.followup.send("ユーザーのブロックが完了しました。\nブロックを解除するには、もう一度`/block`コマンドを実行してください。", ephemeral=True)



async def setup(bot):
  await bot.add_cog(Block(bot))