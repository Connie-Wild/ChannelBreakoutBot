# Channel Breakout Bot for bitflyer-FX

Special Thanks for Snufkin https://sshuhei.com/

<font size="4">
本ソフトウェアの商用利用を禁止します。<br>
ソースコードを改変した物の販売や、設定パラメータの販売も許可しません。<br>
商用利用が発覚した場合、金1000万円を請求致します。<br>
また、商用利用を行った時点でこの支払に同意したものとみなします。<br>
なお、作者は本ソフトウェアによって生じる一切の損害について責任を負いません。<br>
Commercial use is strictly prohibited.
</font>

## インストール方法
1) [python3](https://www.python.org/) をインストール
2) ターミナルからgitリポジトリをクローン

```bash
git clone https://github.com/Connie-Wild/ChannelBreakoutBot.git
```

3) フォルダに移動し、必要なパッケージをインストール<br>

for Windows 10 with Python 3.6.5
```bash
cd ChannelBreakoutBot
pip install -U pip setuptools
pip install pybitflyer requests pandas pubnub tornado matplotlib
```
for ubuntu16.04 with Python 3.5.2
```bash
cd ChannelBreakoutBot
apt-get install -y python3 python3-pip python3-tk libpng-dev libfreetype6-dev
pip3 install -U pip setuptools
pip3 install pybitflyer requests pandas pubnub tornado matplotlib
```
4) インストールフォルダ内の`config_default.json`を`config.json`にリネーム
5) `key`、`secret`フィールドを、取引所から取得したAPIキー、シークレットに置き換える。
6) コンソールから起動

for Windows 10 with Python 3.6.5
```bash
python trade.py
```
for ubuntu16.04 with Python 3.5.2
```bash
python3 trade.py
```

## 最新版へのアップデート方法

インストールフォルダでコンソールから以下を実行。

```bash
git pull
```
## 設定
設定は`config.json`ファイルで行います。

### 全体設定
|Name|Values|Description|
|----|------|-----------|
|product_code|FX_BTC_JPY|取引銘柄の指定。bitflyer-FXのみ対応。|
|key|string|取引所APIのキー|
|secret|string|取引所APIのシークレット|
|line_notify_token|string|[LINE Notify](https://notify-bot.line.me/ja/)による通知を行う場合に、トークンを設定。|
|healthCheck|true/false|取引所のステータスがNORMALとBUSYとVERY BUSY以外の場合、オープンオーダを行わない。(損切りが出来るようにクローズオーダは行う)|
|entryTerm|number|entryTerm期間高値/安値を更新したらオープンシグナル点灯|
|closeTerm|number|closeTerm期間、オープン方向と逆に高値/安値を更新したらクローズシグナル点灯|
|rangePercent|number/null|[option]下記参照|
|rangePercentTerm|number/null|[option]rangePercentTerm期間の値幅の平均値を求め、rangePercentを掛けた値をentryTerm/closeTerm期間の高値/安値から加算/減算する。|
|rangeTerm|number/null|[option]下記参照|
|rangeTh|number/null|[option]レンジ相場でのエントリーを減らすために、rangeTerm期間の値幅(rangeTh)または価格の標準偏差の変動でレンジ相場の判定を行う。|
|waitTerm|number|下記参照|
|waitTh|number|rangeTh円以上の値幅を取った場合，次のwaitTermトレードはロットを1/10に落とす。(大きいトレンドのあとの大きなリバや戻りで損をしやすいため)|
|candleTerm|string|ロウソクの期間を指定。1T(1分足)、5T(5分足)、1H(1時間足)。分はT、時はHで示す。|
|cost|number|バックテストで利用。遅延等で1トレード毎にcost円分のコストが発生するものとして評価を行う。|
|fileName|string|optimizationで使用するOHLCデータのファイル名を指定する。デフォルトは`chart.csv`|
|showFigure|true/false|バックテスト実行時にグラフを表示するか選択。コマンドラインのみの環境では`false`にして下さい。|

## バックテスト
for Windows 10 with Python 3.6.5
```bash
python backtest.py
```
for ubuntu16.04 with Python 3.5.2
```bash
python3 backtest.py
```

## optimization
別途取得したOHLCデータ`fileName`を元に最適な設定値の探索を試みる。  
自動設定はされないため、探索した値を利用したい場合は`config.json`に設定する必要あり。  

for Windows 10 with Python 3.6.5
```bash
python optimization.py
```
for ubuntu16.04 with Python 3.5.2
```bash
python3 optimization.py
```

## optimization用のOHLCデータの取得
for Windows 10 with Python 3.6.5
```bash
python ohlc_get.py > chart.csv
```
for ubuntu16.04 with Python 3.5.2
```bash
python3 ohlc_get.py > chart.csv
```

## FAQ
### Q.どんな設定値を使えば利益を出せますか？
A. バックテスト等を利用し、ご自身で探して下さい。
