# twitter-discord 連携スクリプト

## 背景

1. 誰かがツイートする。
2. 指定されたDiscordに投稿する。

ということをやろうとするのであれば、いろいろツールがあるので

こんなツール作る必要はない。

ところが、引用リツイートを抽出してDiscordに投稿しようとすると

ツールがないらしい。無いなら作ってしまおうというのが背景。

## 実現方法など

その辺のよくあるバッチ処理。

1. 時間になったら起動する
2. 指定したユーザの一番上に来ているツイートを抽出する
3. 直前に実行した比較して、違ってたらURLを組み立てて
4. 気の利いたテキストと一緒に3のURLをDiscordに投稿する。

各種アクセスに必要なトークン、は当然として

気の利いたテキストなんかは、プログラムの外側において、ある程度好き勝手作れるようにする。

## 導入方法

Pipfileがあるので、Pipenv, Pyenvを導入したあと、

```bash
pipenv install
```

でインストール導入できるはず。

configure_sample.jsonをconfigure.jsonに名前を変更し

設定を書き込む。

```json
{
    "twitter_api_key":"Twitter API キー",
    "twitter_api_key_secret": "Twitter API キーシークレット",
    "twitter_bearer_token": "Bearer トークン",
    "twitter_access_token": "Twitter アクセストークン",
    "twitter_access_token_secret": "Twitter アクセストークンシークレット",
    "twitter_id": 12345678, <- Twitterのuser id
    "twitter_screen_name": "sample", <- Twitterでメンションつけるときの名前
    "discord_bot_token" : "Discord のBotトークン",
    "discord_message_target": 9012345678 DiscordのチャンネルID
}
```
最低、twitter_bearer_token, twitter_id, twitter_screen_name, discord_bot_token, discord_message_targetを書けば大丈夫なはず。

### テンプレートの設定

discord_template.txtの中身を好きなものに差し替えればよい。

ただし${twitter_url}は削除しない事!

### 定時処理の設定

Linux系ならcron, Windowsならタスクスケジューラにmain.pyを実行するように仕込む。

```bash
python main.py
```

で実行するので、上のコマンドを実行するだけのシェルスクリプトなどを用意すればすっきりするはず。


## 制限事項

コマンド終了時、

```python
Exception ignored in: <function _ProactorBasePipeTransport.__del__ at 0x0000028A1C9C15A0>
Traceback (most recent call last):
  File "xxxx.pyenv\pyenv-win\versions\3.10.1\lib\asyncio\proactor_events.py", line 116, in __del__
    self.close()
  File "xxxx.pyenv\pyenv-win\versions\3.10.1\lib\asyncio\proactor_events.py", line 108, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "xxxx.pyenv\pyenv-win\versions\3.10.1\lib\asyncio\base_events.py", line 745, in call_soon
    self._check_closed()
  File "xxxx.pyenv\pyenv-win\versions\3.10.1\lib\asyncio\base_events.py", line 510, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
```

というエラーが出るが、コマンド自体は終了しているので、無視しても影響はない。