# _*_ coding: utf-8 _*_
import datetime


def show(df_candleStick, plofits, buy_entry_signals, sell_entry_signals, buy_close_signals, sell_close_signals):
    plot(df_candleStick, plofits, buy_entry_signals,
         sell_entry_signals, buy_close_signals, sell_close_signals, True)


def save(df_candleStick, plofits, buy_entry_signals, sell_entry_signals, buy_close_signals, sell_close_signals, file_name):
    import matplotlib
    matplotlib.use('Agg')
    plot(df_candleStick, plofits, buy_entry_signals, sell_entry_signals,
         buy_close_signals, sell_close_signals, False, file_name)


def plot(df_candleStick, plofits, buy_entry_signals, sell_entry_signals, buy_close_signals, sell_close_signals, is_show, file_name='fig.png'):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    from .mpl_finance import candlestick2_ohlc, volume_overlay

    df = df_candleStick
    # グラフ生成(figsize=グラフサイズx,y)
    fig = plt.figure(figsize=(12, 8))
    fig.autofmt_xdate()
    fig.tight_layout()
    # 1つ目のグラフ(ローソク足)
    ax = plt.subplot(2, 1, 1)
    # ローソク足描画
    candlestick2_ohlc(ax, df["open"], df["high"], df["low"], df["close"], width=0.7, colorup="b", colordown="r")
    # 描画幅の設定
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom - (top - bottom) / 5, top)
    # 出来高の描画
    ax_v = ax.twinx()
    volume_overlay(ax_v, df["open"], df["close"], df["volume"], width=0.7, colorup="g", colordown="g")
    ax_v.set_xlim([0, df.shape[0]])
    ax_v.set_ylim([0, df["volume"].max() * 4])
    ax_v.set_ylabel("Volume")
    # X軸調整
    xdate = [i.strftime('%y-%m-%d %H:%M') for i in df.index]

    def dateformat(x, pos):
        try:
            return xdate[int(x)]
        except IndexError:
            return ''
    locate_size = len(ax.get_xticks())
    ax.xaxis.set_major_locator(ticker.MaxNLocator(locate_size))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(dateformat))

    ax.autoscale_view()
    ax.grid()
    ax.set_ylabel("Price(JPY)")
    # シグナル線
    ymin = min(df["low"]) - 200
    ymax = max(df["high"]) + 200
    ax.vlines([df.index.get_loc(s) for s in buy_entry_signals],
              ymin, ymax, "blue", linestyles='dashed', linewidth=1)
    ax.vlines([df.index.get_loc(s) for s in sell_entry_signals],
              ymin, ymax, "red", linestyles='dashed', linewidth=1)
    ax.vlines([df.index.get_loc(s) for s in buy_close_signals],
              ymin, ymax, "black", linestyles='dashed', linewidth=1)
    ax.vlines([df.index.get_loc(s) for s in sell_close_signals],
              ymin, ymax, "green", linestyles='dashed', linewidth=1)

    # 2つ目のグラフ(収益グラフ)
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(xdate, plofits)
    # 0に横線
    ax2.hlines(y=0, xmin=ax.get_xticks()[0], xmax=ax.get_xticks()[-1],
               colors='k', linestyles='dashed')

    # X軸の範囲を合わせる(candlestick2_ohlc内でxlimが指定されている為)
    ax2.set_xlim(ax.get_xlim())
    ax2.xaxis.set_major_locator(ticker.MaxNLocator(locate_size))
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(dateformat))
    ax2.autoscale_view()
    ax2.grid()
    ax2.set_ylabel("PL(JPY)")

    if is_show:
        plt.show()
    else:
        plt.savefig(file_name)

    plt.close(fig)
