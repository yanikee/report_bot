# report bot!
　サーバー管理者のためのDiscord botです。

## 主な機能
- サーバールールに違反したメッセージなどをサーバー管理者に報告できます。
- 匿名での報告にも対応しており、サーバー管理者はbotを通じて匿名報告に返信することもできます。
- 🆕 匿名でのticket機能

## 設定
### report
reportを送信するチャンネルを設定します。
```
/report config <channel:任意>
```
- channel欄に何も入力しないと、コマンドを実行したチャンネルがreport送信チャンネルに設定されます。</br></br>

### 匿名ticket
匿名ticketを送信するチャンネルを設定, 匿名ticketを開始するbuttonを設置します。
```
/pticket config <config_channel:必須, button_channel:必須>
```

## 使い方
### report
1. サーバールールに違反したメッセージや、不適切なメッセージを右クリック
2. 「アプリ」をクリック
3. 「！【サーバー管理者に報告】」をクリック

### 匿名ticket
1. 匿名ticket開始ボタンをクリック

---

### bot導入リンク
https://discord.com/oauth2/authorize?client_id=1237001692977827920&permissions=326417583168&scope=bot

### サポートサーバー
https://discord.gg/zU8FnMGHg3
