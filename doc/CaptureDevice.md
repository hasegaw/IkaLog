# HDMI キャプチャ機器

本ページは IkaLog 利用のために新たに HDMI キャプチャ機器の購入を
検討されている方向けに、キャプチャ機器の選び方と動作実績がある型番を
紹介します。

#### おことわり

HDMI キャプチャ環境の構築は相性問題なども発生しやすいです。
「本ページで紹介されている型番を導入してもうまく動作しなかった」
という場合でも責任は負いかねますので、あくまで自己責任で検討してください。

<br>
## 動作報告があったキャプチャデバイス

Windows 環境の IkaLog / IkaLog GUI 版との組み合わせ報告があったキャプチャ機器を紹介します。

USB3.0 のキャプチャデバイスを新規購入する場合は、コンピュータの USB3.0 コントローラとの
相性問題がないかメーカーサイトなどでよく確認してください。

| 推奨 | メーカー | 型番 | 仕様 | 備考 |
|----------|------|-----|----|----|
| ★ | SKNET | [SK-MVXU3R](http://www.sknet-web.co.jp/product/mvxu3r/) | 1080p 60fps | デバイス名 "MonsterX U3.0R Capture" <br> USB 3.0 接続タイプ <br> IkaLog 開発に利用 |
| ★ | AVerMedia | [AVT-C875](http://www.avermedia.co.jp/product_swap/avt-c875.html) | 1080p 60fps | USB 3.0 接続タイプ <br> Stream Engine のインストールが必要。ビットレート 60.0Mbps に指定 <br> デバイス名 "LGP Stream Engine" <br> ハードウェア MPEG エンコーダ搭載機 <br> 利用例  [AVT-C875でスプラトゥーンをキャプチャしてみたメモ(IkaLogとWebRTC)](http://mzsm.me/2015/09/23/hdmi-capture-avt-c875/)|
|  | マイコンソフト | [X-CAPTURE 1](http://www.micomsoft.co.jp/xcapture-1.htm) | 1080p 60fps | デバイス名 "???(TBD)" <br> USB 3.0 接続タイプ <br> Twitter 上でアマレコ経由？の動作報告あり |
|  | SKNET | [SK-MVX3](http://www.sknet-web.co.jp/product/mvx3/) | 1080p 24fps | PCIe 拡張カードタイプ <br> デバイス名 "SKNET MonsterX3 HD Capture (Path0)" <br> Twitter上で動作報告あり |
|  | ドリキャプ | [HC-HD1](http://www.drecap.com/DC-HD1BJ.html) | 720p 30fps | PCIe 拡張カードタイプ <br> デバイス名 "7160 HD Capture (Path1)" <br> IkaLog 開発に利用|
|  | サンコー | [HDMVC4UC](http://www.thanko.jp/product/1526.html#introduction) | 1080p 30fps | PCIe 拡張カードタイプ <br> デバイス名 "???(TBD)" <br> 入力画像にズレあり(左に2px)。 offset パラメータ = (2,0) |
|  | CELSUS | [REGIA ONE](http://www.celsus.co.jp/regia/regia1.html) | 1080i | PCIe 拡張カードタイプ <br> デバイス名 "???(TBD)" <br> 入力画像にズレあり(左に2px)。 offset パラメータ = (2,0) |
<br>

Mac環境の IkaLog との組み合わせ報告があったキャプチャ機器を紹介します。

| 推奨 | メーカー | 型番 | 仕様 | 備考 |
|----------|------|-----|----|----|
| ★ | Black Magic<br>Design | [UltraStudio Mini Recorder](https://www.blackmagicdesign.com/jp/store/record-capture-playback/ultrastudiothunderbolt/W-DLUS-04) | 1080p30fps<br>1080i 60fps<br>720p 60fps | Thunderbolt 接続タイプ<br> AVFoundation Input を利用 |

<br>
## IkaLog で使える HDMI キャプチャ機器の条件

Windows 環境で動作する IkaLog (IkaLog GUI)と組み合わせるHDMIキャプチャは下記の条件を満たす必要があります。

####  必須条件
- Windows で動作すること。
- 32bit 版 DirectShow フィルタドライバが提供されていること。
- OpenCV からデバイスが制御できること。

#### 推奨条件

- HDMI キャプチャ内容がおかしい（例：左右フチのドットがかけている、など）は誤認識の原因になります。新しく購入することはあまりオススメしません。
- HDMI パススルー機能を搭載しており、 PC に入力しながら他の TV やディスプレイに映して
  プレイできるものがオススメ。 <br> （もしくは HDMI スプリッタを併用する)
- MPEG 圧縮などを行わず、オリジナル映像に忠実なデータを入力できること。 <br>
  お店の POP などでは「ソフトウェアエンコード」と書かれている場合があります
※ 強者は Linux 環境上で OpenCV に別途パッチを当てて BMD の Intensity Pro と組み合わせて動かしていたりもするようです。 (O_O)

####  「ソフトウェアエンコード」と「ハードウェアエンコード」

ソフトウェアエンコード などとお店などで紹介されているタイプの HDMI キャプチャ機器は、
HDMI からの入力信号を、各ドット、できるだけそのままコンピュータに入力します。コンピュータで
録画する場合は、このデータをそのまま（非圧縮形式で）保存したり、ソフトウェアベースのコーデック
を利用してエンコードすることを想定した製品です。

- エンコードまで含めて行うと、コンピュータへの負荷は大きい
- 遅延が最小限
- エンコードされていないためオリジナルに割と忠実なデータが入力される

これに対して、 ハードウェアエンコード などと紹介されているものは HDMI キャプチャ機器が
MPEG エンコーダの LSI を搭載しており、コンピュータには MPEG エンコードされたデータが
入力されます。（.MP4 ファイルがデバイスからPCに届くようなものと考えてください）

- （録画に使うなら）コンピュータがエンコードしなくてよいため、性能の低いコンピュータでも使える
- 数秒レベルの遅延がある
- エンコードの課程で画像が劣化する

IkaLog の場合は前者のソフトウェアエンコード方式のデバイスをおすすめします。

- 遅延が少ない
- 入力画像がより忠実であり IkaLog が誤動作しにくい
