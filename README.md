# layeredpsdmaterial
layerつきのpsdファイルをblenderにインポートしたり、layerごとの表示制御をする拡張機能
## 機能
* psdファイルのインポート
* インポートしたpsdファイルに対し、各layerごとの表示制御
  * layer名が"\*"で始まる場合、同階層で1つだけ表示
  * layer名が"!"で始まる場合、必ず表示する
## 動作環境
* Blender 2.93LTS~
またプラグイン内で以下のpythonパッケージを利用しています
* Numpy
* Pillow
* psd-tools
## 既知の問題点
* 1グループに33枚以上のlayerがあるとバグる
  * blenderのenum型の制約に引っかかっている
* psdファイル読み込み時、平面を追加する場合に座標設定できない
* layerの表示状態変更時の処理が重い
  * 依存先のpsd-toolsのpsd.compose()を同期で呼び出しているため&psd-toolsが重め
  * 依存先ライブラリを変えれば解決するか?
## 対応予定
* 33枚以上1layerにある場合の問題対応
* 画像生成処理に使うライブラリを変えるか非同期にする
## 導入手順
1. [Releases](https://github.com/simanasch/layeredPsdMaterial/releases)をクリック
2. リンク先からzipファイルをダウンロード
3. blenderを開き、「編集」→「プリファレンス」→「アドオン」の順に開く
4. 「インストール」をクリックし、2.でダウンロードしたzipファイルを選択
5. プリファレンス画面で有効化
導入後、オブジェクトに対し「Psd Material」タブが追加されます
