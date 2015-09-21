# Embedded IkaLog

IkaLog のコア部分は IkaEngine クラスとしてまとまっています。
このクラスを自前で初期化してあげることで、自分の好きな Python プログラムに IkaLog をエンベッド動作させることもできなくはありません。

このような利用はこれまで想定してこなかったので、細かな問題が発生することは
承知の上利用を検討してください。

## サンプル

utils/IkaRename.py を読んでみてください。

IkaRename.py はビデオファイルを再生し、そのビデオファイルでの Splatoon プレイ内容をもとに
ビデオファイル名をリネームする例です。

## IkaLog Engine の初期化

このプラグインのコンストラクタ内で IkaEngine を初期化して動かしましょう。

````Python
    def __init__(self, file):
        input = IkaInput_CVCapture()
        input.startRecordedFile(file)
        input.need_resize = True #1280x720 に入力ソースを強制変更

	# IkaEngine からのコールバックを受けるのは自分
        outputPlugins = [ self ]

        # IkaEngine を実行
        self.engine = IkaEngine()

	# インプット、アウトプットプラグインを設定
        self.engine.setCapture(input)
        self.engine.setPlugins(outputPlugins)

	# ポーズ状態を解除
        self.engine.pause(False)
        self.engine.run()
````

## プラグインインターフェイスで通知を拾う

IkaLog の基本はプラグインに対するコールバックです。なのでプラグインを受けるクラスを作ります。

````Python
class MyClass:

    def onGameIndividualResult(self, context):
        print('組み込まれた IkaLog のなかで戦績が検出されました')
````

本ドキュメント執筆時点では、 IkaLog がビデオファイルの最後に到達すると onFrameReadError コールバックが呼ばれます。
本コールバックが発生したら IkaEngine の stop() メソッドを呼び出して IkaEngine をメインループから脱出させます。

````Python
    def onFrameReadFailed(self, context):
        print('%s: たぶんファイルの終端にたどり着きました' % self.file)
        # もういいので IkaEngine を止める
````

これで、 IkaLog でビデオを再生して戦績画面が表示されたらメッセージを表示するクラスができました。

## メイン

このクラスを呼び出します。

````Python
if __name__ == "__main__":
   IkaRename(sys.argv[1])
````
