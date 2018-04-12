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
5) インストールフォルダ内の`optimizeList_default.json`を`optimizeList.json`にリネーム
6) `key`、`secret`フィールドを、取引所から取得したAPIキー、シークレットに置き換える。
7) コンソールから起動

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
|cost|number|バックテストおよび、optimizationで利用。遅延等で1トレード毎にcost円分のコストが発生するものとして評価を行う。|
|fileName|string/null|バックテストおよび、optimizationで使用するOHLCデータのファイル名を指定する。デフォルトは`chart.csv`。指定が無い場合は都度取得する。|
|showFigure|true/false|バックテスト実行時にグラフを表示するか選択。コマンドラインのみの環境では`false`にして下さい。|
|sendFigure|true/false|バックテスト結果のグラフをLINE Notifyで通知する。`showFigure`が`false`の場合のみ有効。|
|core|number/null|optimizationで使用するCPUコア数を指定。`null`の場合、全てのコアを利用する。`1`の場合、パラメータ毎の詳細実行結果を表示するが、`2`以上または`null`の場合は、パラメータ毎の実行結果は簡易表示となる。(全てのコアを利用するとCPU使用率が100%に張り付くため、全体コア数-1の値を設定する事をオススメする。)|
|showTradeDetail|true/false|バックテストの結果として、トレード履歴の詳細を表示する。|

## バックテスト
別途取得したOHLCデータ`fileName`を元にバックテストを行う。  
`fileName`の指定が無い場合は`cryptowat.ch`から都度取得する。   

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
`fileName`の指定が無い場合は`cryptowat.ch`から都度取得する。(都度取得すると時間がかかる上に同じOHLCデータでの比較が出来ないので`fileName`の指定をする事をオススメします。)  
自動設定はされないため、探索した値を利用したい場合は`config.json`に設定する必要あり。  

for Windows 10 with Python 3.6.5
```bash
python optimization.py
```
for ubuntu16.04 with Python 3.5.2
```bash
python3 optimization.py
```
## optimization用のパターンデータの用意
設定は`optimizeList.json`ファイルで行います。

### パターンデータ
|Name|Values|Description|
|----|------|-----------|
|entryAndCloseTerm|number|[entryTerm,closeTerm]で指定。|
|rangeThAndrangeTerm|number/null|[rangeTh,rangeTerm]で指定。|
|waitTermAndwaitTh|number|[waitTerm,waitTh]で指定。|
|rangePercentList|number/null|[rangePercent,rangePercentTerm]で指定。|

## optimization用のOHLCデータの取得
コマンドライン引数に取得したい日付と取得時間足を指定する事が出来る。  
時間足：1分足 = 60 , 1時間足 = 3600  
日付：yyyy-mm-dd  
例)5分足を最新から6000件取得する。  
`ohlc_get.py 300`  
例)2018-04-05の5分足を取得する。  
`ohlc_get.py 300 2018-04-05`  
引数を指定しない場合、1分足データを6000件取得する。  

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
