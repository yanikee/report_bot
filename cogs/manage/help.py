from discord.ext import commands
from discord import app_commands
import discord



class Help(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="help", description='helpコマンドです。')
  async def report(self, interaction:discord.Interaction):
    embed = discord.Embed(
      title="Help! (1/4)",
      description="このbotには2つの機能があります。\n\n"
                  "1. __Report機能__\n"
                  " - ルール違反したメッセージ投稿などを、簡単にサーバー管理者に報告できる機能\n"
                  "2. __匿名Ticket機能__\n"
                  " - 『Ticket Tool』の匿名版の様な機能",
      color=0xF4BD44,
    )

    view = discord.ui.View()
    button_0 = discord.ui.Button(label="まず何をすればいいの？(設定方法)", emoji="⚙️", custom_id=f"quickstart", style=discord.ButtonStyle.primary, row=0)
    button_1 = discord.ui.Button(label="使い方を知りたい！", emoji="✊", custom_id=f"how_to_use", style=discord.ButtonStyle.green, row=1)
    button_2 = discord.ui.Button(label="その他", emoji="💪", custom_id=f"others", style=discord.ButtonStyle.gray, row=1)
    view.add_item(button_0)
    view.add_item(button_1)
    view.add_item(button_2)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)



  @commands.Cog.listener()
  async def on_interaction(self, interaction):
    try:
      if not interaction.data["custom_id"] in ["quickstart", "how_to_use", "others"]:
        return
    except KeyError:
      return


    if interaction.data["custom_id"] == "quickstart":
      embed=discord.Embed(
        title="Help! (2/4)",
        description="## まず何をすればいいの？(設定方法)\n"
                    "### Report機能\n"
                    "- __**`/report config` を実行**__\n"
                    " - Reportを受信するチャンネルを設定します\n"
                    " - Reportを受け取りたいチャンネルで実行\n"
                    "### 匿名Ticket機能\n"
                    "- __**`/pticket config` を実行**__\n"
                    " - 匿名Ticketを受信するチャンネル，匿名Ticketを開始するためのボタンを設置するチャンネル を指定します。\n"
                    " - 匿名Ticketを開始するためのボタンを設置したいチャンネルで実行\n\n"
                    "- 詳しくは[こちら](https://yanikee.github.io/report_bot-docs2/docs/quickstart/)\n"
                    "- 画像付きで解説しています",
        color=0xF4BD44,
      )
      await interaction.response.edit_message(embed=embed)

    elif interaction.data["custom_id"] == "how_to_use":
      embed=discord.Embed(
        title="Help! (3/4)",
        description="## 使い方を知りたい！\n"
                    "### Report機能\n"
                    "1. 報告したいメッセージを右クリック\n"
                    "2. 「アプリ」\n"
                    "3. 【サーバー管理者に報告】\n"
                    "### 匿名Ticket機能\n"
                    "1. 匿名Ticketボタンをクリック\n"
                    " - サーバー管理者が設置します\n"
                    " - 存在しなかったら、サーバー管理者さんに聞いてみてください",
        color=0xF4BD44,
      )
      await interaction.response.edit_message(embed=embed)

    elif interaction.data["custom_id"] == "others":
      embed=discord.Embed(
        title="Help! (4/4)",
        description="## その他のコマンド！\n"
                    "## `/block`\n"
                    "- 匿名Report, Ticketのユーザーによる返信をブロックできる機能\n"
                    "- 本botを悪用した荒らしなどが行われた場合にご活用ください。\n",
        color=0xF4BD44,
      )
      await interaction.response.edit_message(embed=embed)



async def setup(bot):
  await bot.add_cog(Help(bot))