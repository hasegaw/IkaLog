# プラグイン開発

IkaLog のアクションはプラグインで定義します。このドキュメントではプラグインの作り方について説明します。

なお、現在 IkaLog は大変カジュアルに開発されています。
このドキュメントの内容が変更されること、このドキュメントの後に仕様が変更されることもあります。

#＃ プラグインの実態

IkaLog のプラグインの正体は Python のクラスです。

- ひとつのプラグインは、ひとつの Python クラスのオブジェクト

## プラグインとして最低限必要なもの

IkaLog がプラグインとして扱える最低限の実装は下記のとおりです。

````Python
class IkaOutput_MyPlugin:
    # 何もいらないけど、実行できないので
    dummy = True
````

## コンストラクタ

クラスのコンストラクタは以下の2タイプの呼び出しが可能な作りとします。

- 引数なし(プラグインの設定が空である)
- 引数あり(プラグインのパラメータが引数として渡される)

コンソール版 IkaLog では、現在、プラグインの設定は各クラスのコンストラクタに引数として
渡されています。このためコンソール版 IkaLog で動作するためには引数がとれる必要があります。

GUI 版 IkaLog では、現在、プラグインは引数なしで初期化ののち onResetConfig() メソッド
が呼び出されます。このため GUI 版 IkaLog で動作するためには引数がない状態でも
コンストラクタが呼び出せなくてはなりません。

究極的には、オプションが一切不要なプラグインであれば、 __init__() を定義する必要性はありません。

````Python
Class IkaOutput_OBS:
    def __init__(self, ControlOBS = None, dir = None):
        self.enabled = (not ControlOBS is None)
        self.AutoRenameEnabled = (not dir is None)
        self.ControlOBS = ControlOBS
        self.dir = dir
````

## IkaEngine にプラグインを登録する

IkaEngine に新しいプラグインを登録するには、 IkaEngine.setPlugins() メソッドで
新しいプラグインオブジェクトのリストを渡します。

コンソール版 IkaLog の場合は IkaConfig.py の中でプラグインオブジェクトのリストを作成しています。

IkaUI の場合は IkaUI.py の中でハードコードしています。


## コールバックを受ける

IkaLog が何かの場面を検出すると、プラグインが持っているコールバックが実行されます。
コールバックのリストを下記に示します。

| メソッド名 | 場面 |
|------------|------|
| onFrameRead | 入力ソースから（間引きされた）フレームが読み込まれた |
| onLobbyMatching | 待ち合わせロビー。プレイヤーはまだ8人揃っていない |
| onLobbyMatched | 待ち合わせロビー。 プレイヤーが8人揃い、間もなくゲーム開始 |
| onGameStart | ゲームのステージとルールが判明した |
| onGameGoSign | ゲーム開始の合図(Go!) の瞬間 |
| onGameFinish | ゲーム終了（タイムアップもしくはノックアウト）の瞬間 |
| onGameDead |  IkaLog ユーザーのインクリングが死亡 |
| onGameIndividualResultAnalyze | 戦績画面(K/D)が表示された |
| onGameIndividualResult | 戦績画面(K/D)が表示され、分析が完了 |
| onGameReset | 一回のゲームが完了した。次のイベントからは別のゲームと見なす |

これらのコールバックは下記の引数で呼び出されます。

````Python
plugin.onGameStart(context)
````

このため各コールバックは下記のとおり定義しなければなりません。

````
class IkaOutput_MyPlugin:
    def onGameStart(self, context):
````

#### コールバックが呼ばれないこともある

コールバックは認識失敗などの理由で呼び出しが漏れたりすることも考えられます。
プラグインを作成するときは、意図したタイミングでコールバックが呼ばれなくても
停止したり、極端な誤動作はしないようにすべきです。

#### プラグイン内での例外

コールバック関数から例外が上がると、 IkaEngine はその例外のバックトレースを表示して
そのまま実行を続けます。このためコールバック内の例外程度では   IkaLog の動作が止まることは基本的にはありません。

## コンテクストから状態を知る

context は、 IkaLog のエンジンである IkaEngine が持つコンテクストオブジェクト
(Dict型) が渡されています。このオブジェクトを調べることで IkaLog が認識している
状況がわかります。

| context | 説明 |
|---------|------|
| context['engine'] | IkaEngine が管理 |
| context['engine']['frame'] | 現在処理中のフレーム(1280x720 BGR画像) |
| context['engine']['msec'] | 現在のメディア情報(ミリ秒単位) |
| context['engine']['inGame'] | 試合中か（左上に時計が出ているか。水没中など出ていない場合はマッチしないため注意） |
| context['lobby']['type'] | マッチングのタイプ。 野良(public)、タッグマッチ(tag)、フェスマッチ(festa) |
| context['lobby']['state'] | マッチングの途中(matching) か、マッチング完了(matched) か |
| context['game'] | ゲーム進行状況のステート |
| context['game']['map'] | 現在のステージを示すオブジェクト |
| context['game']['rule'] | 現在のルールを示すオブジェクト |
| context['game']['won'] | ゲームに勝ったか、負けたか |
| context['game']['players'] | 戦績画面に表示されたプレイヤーのリスト |
| context['config'] | 各プラグインの設定値などが保存される |
| context['config']['plugin1']['var1'] | プラグイン plugin1 の設定 var1 |

まだ他にもありますがソースコードをたどってみてください。

#### コンテキストからステージ名を知る

````Python
map = IkaUtils.map2text(context['game']['map'])
rule = IkaUtils.rule2text(context['game']['rule'])
print('ステージ %s ルール名 %s ' % (map2, rule2))

map2 = IkaUtils.map2text(context['game']['map'], unknown = 'スプラトゥーン')
rule2 = IkaUtils.rule2text(context['game']['rule'], unknown = 'バトル')
print('%s で %s を遊びました' % (map2, rule2))

````

#### 勝敗を知る

````Python
    def onGameIndividualResult(self, context):
        result         = IkaUtils.getWinLoseText(context['game']['won'])
        human_readable = IkaUtils.getWinLoseText(context['game']['won'], win_text ='勝ち', lose_text = '負け', unknown_text = '不明')
        for_database   = IkaUtils.getWinLoseText(context['game']['won'], win_text ='win', lose_text = 'lose', unknown_text = 'unknown')
        in_english     = IkaUtils.getWinLoseText(context['game']['won'], win_text ='win', lose_text = 'defeat', unknown_text = 'unknown')
````

#### スクリーンショットを保存する

````Python
IkaUtils.writeScreenshot('i_was_the_hero.png', context['engine']['frame'])
````


## GUI に対応する

IkaUI による GUI で動作する場合は、追加のコールバックが利用されます。

| メソッド名 | 場面 |
|------------|------|
| onConfigApply | GUI上に入力された設定値を反映するべきタイミング |
| onConfigReset | 設定値をリセットするべきタイミング |
| onConfigSaveToContext | 各プラグインが context['config'] から自身の設定値をロードするべきタイミング |
| onConfigLoadFromContext | 各プラグインが context['config'] へ自身の設定値をセーブするべきタイミング |
| onOptionTabCreate | IkaUI の Options タブを生成するタイミング |


### wxPython

IkaUI は wxPython で実装されています。プラグインは GUI で動作する場合に
wxPython を import する必要があるでしょう。

````Python
try:
        import wx
except:
        pass # コンソール環境ではなくても動作する
````

### onOptionTabCreate

呼び出されるときの引数が他のプラグインと違いますので注意が必要です。(今後どうするか未定)

第一引数に IkaUI の Options (wx.Notebook) が渡されますので、ノートブックに
ページを追加し、内部にパネルおよび設定用の UI コンポーネントを配置するコードを書きます。

````Python
def onOptionTabCreate(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, 'OBS')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'Open Broadcaster Software の録画／録画停止ボタンを自動操作する')
        self.checkAutoRenameEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'録画ファイルの自動リネームを行う')
        self.editControlOBS = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editDir = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'ControlOBS.au3 パス'))
        self.layout.Add(self.editControlOBS, flag = wx.EXPAND)
        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'録画フォルダ'))
        self.layout.Add(self.editDir, flag = wx.EXPAND)

        self.layout.Add(self.checkEnable)
        self.layout.Add(self.checkAutoRenameEnable)
````

### コールバックから wxPython オブジェクトを操作してはいけない

IkaUI では、 IkaEngine はサブスレッドとして実行されています。
このため IkaEngine はサブスレッド内でプラグインのコールバックを呼び出します。

wxPython のオブジェクトメインスレッドからでなければ操作ができないため、
IkaEngine から呼び出されたコールバックから wxPython のオブジェクトを操作すると
IkaUI がクラッシュします。

対策方法として、メインスレッドで動作する IkaUI クラスからの呼び出しタイミングを使うか、
wx.Timer クラスで定期的にメインスレッド上でコールバックを受けてください。

また、これだけではインターフェイスとして不十分なのは承知していますので、
メインスレッドでコールバックを提供する方法の提案や Pull Request なども歓迎です。
