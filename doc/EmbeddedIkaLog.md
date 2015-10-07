# Embedded IkaLog

IkaLog のコア部分は ikalog モジュールとしてしてまとまっています。
このクラスを自前で初期化してあげることで、自分の好きな Python プログラムに IkaLog をエンベッド動作させることもできなくはありません。

このような利用はこれまで想定してこなかったので、細かな問題が発生することは
承知の上利用を検討してください。

本ページの内容は関数名が PEP8 準拠に変更される前のもので書かれています。

## サンプル

| サンプル名 | 説明 |
|------------|------|
| tools/IkaRename.py | スプラトゥーンプレイ動画のマップ、勝敗を解析し、動画ファイル名に反映する |
| tools/IkaClips.py | スプラトゥーンプレイ動画からゲーム開始、キル・デス、終了のみを抜き出したサマリ動画を生成する |

## IkaLog Engine の初期化

このプラグインのコンストラクタ内で ikalog.engine を初期化して動かしましょう。

````Python
    def __init__(self, filename):
        source = inputs.CVCapture()
        source.start_recorded_file(filename)
        source.need_resize = True #1280x720 に入力ソースを強制変更

	# IkaEngine からのコールバックを受けるのは自分
        output_plugins = [ self ]

        # IkaEngine を実行
        self.engine = engine()

	# インプット、アウトプットプラグインを設定
        self.engine.set_capture(source)
        self.engine.set_plugins(output_plugins)

	# ポーズ状態を解除
        self.engine.pause(False)
        self.engine.run()
````

## プラグインインターフェイスで通知を拾う

IkaLog の基本はプラグインに対するコールバックです。なのでプラグインを受けるクラスを作ります。

````Python
class MyClass:

    def on_game_individual_result(self, context):
        print('組み込まれた IkaLog のなかで戦績が検出されました')
````

本ドキュメント執筆時点では、 IkaLog がビデオファイルの最後に到達すると onFrameReadError コールバックが呼ばれます。
本コールバックが発生したら IkaEngine の stop() メソッドを呼び出して IkaEngine をメインループから脱出させます。

````Python
    def on_frame_read_failed(self, context):
        print('%s: たぶんファイルの終端にたどり着きました' % self.file)
        # もういいので IkaEngine を止める
````

これで、 IkaLog でビデオを再生して戦績画面が表示されたらメッセージを表示するクラスができました。

## メイン

このクラスを呼び出します。

````Python
if __name__ == "__main__":
   MyClass(sys.argv[1])
````
