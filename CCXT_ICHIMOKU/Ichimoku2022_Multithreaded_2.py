import sys

import os
import ccxt
import pandas as pd
from datetime import datetime
import time
import threading
import ta
import argparse
import signal
from datetime import date

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', True)


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    os.kill(os.getpid(), 9)
    sys.exit(-888)


signal.signal(signal.SIGINT, signal_handler)


def log_to_errors(str_to_log):
    fr = open("errors.txt", "a")
    fr.write(str_to_log + "\n")
    fr.close()


def log_to_results(str_to_log):
    fr = open("results.txt", "a")
    fr.write(str_to_log + "\n")
    fr.close()


def log_to_results_evol(str_to_log):
    fr = open("results_evol.txt", "a")
    fr.write(str_to_log + "\n")
    fr.close()


def delete_results_log():
    if os.path.exists("results.txt"):
        os.remove("results.txt")


def delete_results_evol_log():
    if os.path.exists("results_evol.txt"):
        os.remove("results_evol.txt")


def delete_errors_log():
    if os.path.exists("errors.txt"):
        os.remove("errors.txt")


def log_to_results_temp(str_to_log, exchange_id):
    fr = open("results_temp_" + exchange_id + ".txt", "a")
    fr.write(str_to_log + "\n")
    fr.close()


def delete_results_temp_log(exchange_id):
    if os.path.exists("results_temp_" + exchange_id + ".txt"):
        os.remove("results_temp_" + exchange_id + ".txt")


delete_errors_log()

exchanges = {}  # a placeholder for your instances
for id in ccxt.exchanges:
    exchange = getattr(ccxt, id)
    exchanges[id] = exchange()
    # print(exchanges[id])
    try:
        ex = exchanges[id]
        # markets = ex.fetch_markets()
        # print(markets)
    except:
        continue


# function not used for now (but might be useful for a counter such as 1/xxx 2/xxx etc...)
def get_number_of_active_assets_for_exchange(exchange_id):
    nb_active_assets = 0
    arg_exchange = exchange_id
    if arg_exchange in exchanges:
        exchange = exchanges[arg_exchange]
        try:
            markets = exchange.fetch_markets()
            for oneline in markets:
                symbol = oneline['id']
                active = oneline['active']
                if active is True:
                    # print(symbol, end=' ')
                    nb_active_assets += 1
            # print("")
            # print("number of active assets =", nb_active_assets)
        except (ccxt.ExchangeError, ccxt.NetworkError, ccxt.DDoSProtection):
            print("Exchange seems not available (maybe too many requests). Will stop now.")
            # exit(-10002)
            os.kill(os.getpid(), 9)
            sys.exit(-999)
            # time.sleep(5)
        except:
            print(sys.exc_info())
            exit(-10003)
    return nb_active_assets


# print(get_number_of_active_assets_for_exchange("binance"))
# exit(-1000)

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--exchange", help="set exchange", required=False)
parser.add_argument('-g', '--get-exchanges', action='store_true', help="get list of available exchanges")
parser.add_argument('-a', '--get-assets', action='store_true', help="get list of available assets")
parser.add_argument('-f', '--filter-assets', help="assets filter")
parser.add_argument('-r', '--retry', action='store_true', help="retry until exchange is available (again)")
parser.add_argument('-gotc', '--getting-over-the-cloud', action='store_true',
                    help="scan for assets getting over the cloud")
parser.add_argument('-gutc', '--getting-under-the-cloud', action='store_true',
                    help="scan for assets getting under the cloud")
parser.add_argument('-hgotc', '--has-got-over-the-cloud', action='store_true',
                    help="scan for assets that have got over the cloud")
#todo add -hgutc
parser.add_argument('-gotk', '--getting-over-the-kijun', action='store_true',
                    help="scan for assets getting under the cloud")
parser.add_argument('-gutk', '--getting-under-the-kijun', action='store_true',
                    help="scan for assets getting under the cloud")
parser.add_argument('-hgotk', '--has-got-over-the-kijun', action='store_true',
                    help="scan for assets that have got over the kijun")
#todo add -hgutk
parser.add_argument('-gott', '--getting-over-the-tenkan', action='store_true',
                    help="scan for assets getting under the tenkan")
parser.add_argument('-gutt', '--getting-under-the-tenkan', action='store_true',
                    help="scan for assets getting under the tenkan")
parser.add_argument('-cvup', '--chikou-validated-up', action='store_true',
                    help="scan for assets having their chikou validated in uptrend (over all its Ichimoku levels)")
parser.add_argument('-cvdown', '--chikou-validated-down', action='store_true',
                    help="scan for assets having their chikou validated in downtrend (under all its Ichimoku levels)")
parser.add_argument('-pvup', '--price-validated-up', action='store_true',
                    help="scan for assets having their price validated in uptrend (over all its Ichimoku levels)")
parser.add_argument('-pvdown', '--price-validated-down', action='store_true',
                    help="scan for assets having their price validated in downtrend (under all its Ichimoku levels)")
parser.add_argument('-iotc', '--is-over-the-cloud', action='store_true',
                    help="scan for assets being over the cloud")
parser.add_argument('-iutc', '--is-under-the-cloud', action='store_true',
                    help="scan for assets being under the cloud")
parser.add_argument('-t', '--trending', action='store_true',
                    help="scan for trending assets (that are ok in at least 1m or 3m or 5m or 15m) ; only these will be written to the results log file")
parser.add_argument('-l', '--loop', action='store_true', help="scan in loop (useful for continually scan one asset or a few ones)")

args = parser.parse_args()
print("args.exchange =", args.exchange)
print("args.get-exchanges", args.get_exchanges)
print("args.get-assets", args.get_assets)
print("args.filter", args.filter_assets)
print("args.retry", args.retry)
print("args.getting-over-the-cloud", args.getting_over_the_cloud)
print("args.getting-under-the-cloud", args.getting_under_the_cloud)
print("args.has-got-over-the-cloud", args.has_got_over_the_cloud)
print("args.getting-over-the-kijun", args.getting_over_the_kijun)
print("args.getting-under-the-kijun", args.getting_under_the_kijun)
print("args.has-got-over-the-kijun", args.has_got_over_the_kijun)
print("args.getting-over-the-tenkan", args.getting_over_the_tenkan)
print("args.getting-under-the-tenkan", args.getting_under_the_tenkan)
print("args.chikou-validated-up", args.chikou_validated_up)
print("args.chikou-validated-down", args.chikou_validated_down)
print("args.price-validated-up", args.price_validated_up)
print("args.price-validated-down", args.price_validated_down)
print("args.is-over-the-cloud", args.getting_over_the_cloud)
print("args.is-under-the-cloud", args.getting_under_the_cloud)
print("args.trending", args.trending)
print("args.loop", args.loop)

print("INELIDA Scanner v1.0 - https://twitter.com/IchimokuTrader")
print("Scan started at :", str(datetime.now()))

# if a debugger is attached then set arbitrary arguments for debugging (exchange...)
if sys.gettrace() is not None:
    args.exchange = "binanceus"
    args.filter_assets = "*usdt"
    args.loop = False

if args.get_exchanges is True:
    for id in ccxt.exchanges:
        print(id, end=' ')
    print("")
    exit(-505)

if args.get_assets is True:
    if args.exchange is None:
        print("Please specify an exchange name")
    else:
        arg_exchange = args.exchange.lower().strip()
        if arg_exchange in exchanges:
            exchange = exchanges[arg_exchange]
            try:
                markets = exchange.fetch_markets()
                nb_active_assets = 0
                for oneline in markets:
                    symbol = oneline['id']
                    active = oneline['active']
                    if active is True:
                        print(symbol, end=' ')
                        nb_active_assets += 1
                print("")
                print("number of active assets =", nb_active_assets)
            except (ccxt.ExchangeError, ccxt.NetworkError, ccxt.DDoSProtection):
                print("Exchange seems not available (maybe too many requests). Will stop now.")
                # exit(-10002)
                os.kill(os.getpid(), 9)
                sys.exit(-999)
                # time.sleep(5)
            except:
                print(sys.exc_info())
                exit(-10003)
    exit(-510)

filter_assets = ""
if args.filter_assets is not None:
    if args.filter_assets.strip() != "":
        filter_assets = args.filter_assets.strip().upper()
        if ("*" in filter_assets and filter_assets.startswith("*") == False and filter_assets.endswith("*") == False) \
                or (
                "*" in filter_assets and filter_assets.startswith("*") == True and filter_assets.endswith("*") == True):
            print(
                "Only one '*' wildcard must be at the start or at the end of the string and not in the middle (not supported).")
            exit(-10004)

retry = args.retry

getting_over_the_cloud = args.getting_over_the_cloud
getting_under_the_cloud = args.getting_under_the_cloud
has_got_over_the_cloud = args.has_got_over_the_cloud
getting_over_the_kijun = args.getting_over_the_kijun
getting_under_the_kijun = args.getting_under_the_kijun
has_got_over_the_kijun = args.has_got_over_the_kijun
getting_over_the_tenkan = args.getting_over_the_tenkan
getting_under_the_tenkan = args.getting_under_the_tenkan
is_over_the_cloud = args.is_over_the_cloud
is_under_the_cloud = args.is_under_the_cloud
chikou_validated_up = args.chikou_validated_up
chikou_validated_down = args.chikou_validated_down
price_validated_up = args.price_validated_up
price_validated_down = args.price_validated_down

trending = args.trending
print("trending=", trending)

loop_scan = args.loop

# end of arguments parsing here

debug_delays = False
delay_thread = 0.1  # delay between each start of a thread (in seconds, eg. 0.5 for 500ms, 1 for 1s...)
delay_request = 0.250  # delay between each request inside of a thread

exchange = None
if args.exchange is not None:
    arg_exchange = args.exchange.lower().strip()
    if arg_exchange in exchanges:
        print(arg_exchange, "is in list")
        exchange = exchanges[arg_exchange]
        # exit(-1)
    else:
        print("This exchange is not supported.")
        exit(-1)
else:
    print("no exchange specified.")
    exit(-2)

delete_results_temp_log(exchange.id)

# exchange = ccxt.binance()
# exchange = ccxt.ftx()

# for tf in exchange.timeframes:
#     print(tf)

# binance.timeframes {'1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m', '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h', '1d': '1d', '3d': '3d', '1w': '1w', '1M': '1M'}
# exchange.set_sandbox_mode(True)


def get_data_for_timeframe(symbol, tf):
    result = exchange.fetch_ohlcv(symbol, tf, limit=52 + 26)
    return result

def check_timeframe(symbol, tf):
    if (ssb > ssa and price_open > ssb and price_close > ssb) or (ssa > ssb and price_open > ssa and price_close > ssa):
        pass#print(symbol, tf, "**** is over the cloud")
        if (price_close > kijun):
            pass#print(symbol, tf, "******** is over the kijun")
            if (price_close > tenkan):
                pass#print(symbol, tf, "************ is over the tenkan")
                if (chikou > ssa_chikou and chikou > ssb_chikou and chikou > price_high_chikou and chikou > tenkan_chikou and chikou > kijun_chikou):
                    pass#print(symbol, tf, "**************** has chikou validated")
                    if (price_close > ssa and price_close > ssb and price_close > tenkan and price_close > kijun and price_close > price_open):
                        pass#print(symbol, tf, "******************** has price validated")
                        return True



dict_results = {}
dict_results_binary = {}
dict_results_evol = {}
highest_percent_evol = 0


def execute_code(symbol, type_of_asset, exchange_id):
    global dict_results, highest_percent_evol
    global ssb, ssa, price_open, price_close, kijun, tenkan, chikou, ssa_chikou, ssb_chikou, price_high_chikou, price_low_chikou
    global tenkan_chikou, kijun_chikou

    # print(10 * "*", symbol, type_of_asset, exchange.id, 10 * "*")

    key = symbol + " " + type_of_asset + " " + exchange_id

    price_open_1d = None
    price_high_1d = None
    price_low_1d = None
    price_close_1d = None
    s_price_open_1d = ""
    s_price_high_1d = ""
    s_price_low_1d = ""
    s_price_close_1d = ""
    percent_evol_1d = None
    s_percent_evol_1d = ""

    binary_result = ""

    #print("Available timeframes : ", exchange.timeframes)

    for tf in exchange.timeframes:

        if exchange_id in ("binance", "gateio") :
            if not symbol.endswith('USDT'):
                continue
        elif exchange_id == "bybit":
            if not symbol.endswith('PERP'):
                continue

        if tf != "15m":
            continue
        #else:
            #print("Processing 1m for", symbol)

        try:

            #result = exchange.fetch_ohlcv(symbol, tf, limit=52 + 26)
            result = get_data_for_timeframe(symbol, tf)
            #print(tf, symbol, result)
            dframe = pd.DataFrame(result)
            # print(dframe[0])  # UTC timestamp in milliseconds, integer
            # print(dframe[1])
            # print(dframe[2])
            # print(dframe[3])
            # print(dframe[4])

            dframe['timestamp'] = pd.to_numeric(dframe[0])
            dframe['open'] = pd.to_numeric(dframe[1])
            dframe['high'] = pd.to_numeric(dframe[2])
            dframe['low'] = pd.to_numeric(dframe[3])
            dframe['close'] = pd.to_numeric(dframe[4])

            if tf == "1d":
                price_open_1d = dframe['open'].iloc[-1]
                price_high_1d = dframe['high'].iloc[-1]
                price_low_1d = dframe['low'].iloc[-1]
                price_close_1d = dframe['close'].iloc[-1]

            dframe['ICH_SSB'] = ta.trend.ichimoku_b(dframe['high'], dframe['low'], window2=26, window3=52).shift(26)
            # print(dframe['ICH_SSB'])

            dframe['ICH_SSA'] = ta.trend.ichimoku_a(dframe['high'], dframe['low'], window1=9, window2=26).shift(26)
            # print(dframe['ICH_SSA'])

            dframe['ICH_KS'] = ta.trend.ichimoku_base_line(dframe['high'], dframe['low'])
            # print(dframe['ICH_KS'])

            dframe['ICH_TS'] = ta.trend.ichimoku_conversion_line(dframe['high'], dframe['low'])
            # print(dframe['ICH_TS'])

            dframe['ICH_CS'] = dframe['close'].shift(-26)
            # print(dframe['ICH_CS'])

            ssb = dframe['ICH_SSB'].iloc[-1]
            ssa = dframe['ICH_SSA'].iloc[-1]
            kijun = dframe['ICH_KS'].iloc[-1]
            tenkan = dframe['ICH_TS'].iloc[-1]
            chikou = dframe['ICH_CS'].iloc[-27]
            # print("SSB", ssb)  # SSB at the current price
            # print("SSA", ssa)  # SSB at the current price
            # print("KS", kijun)  # SSB at the current price
            # print("TS", tenkan)  # SSB at the current price
            # print("CS", chikou)  # SSB at the current price

            price_open = dframe['open'].iloc[-1]
            price_high = dframe['high'].iloc[-1]
            price_low = dframe['low'].iloc[-1]
            price_close = dframe['close'].iloc[-1]
            # print("price_open", price_open)
            # print("price_high", price_high)
            # print("price_low", price_low)
            # print("price_close", price_close)

            price_open_chikou = dframe['open'].iloc[-27]
            price_high_chikou = dframe['high'].iloc[-27]
            price_low_chikou = dframe['low'].iloc[-27]
            price_close_chikou = dframe['close'].iloc[-27]
            # print("price_open_chikou", price_open_chikou)
            # print("price_high_chikou", price_high_chikou)
            # print("price_low_chikou", price_low_chikou)
            # print("price_close_chikou", price_close_chikou)

            tenkan_chikou = dframe['ICH_TS'].iloc[-27]
            kijun_chikou = dframe['ICH_KS'].iloc[-27]
            ssa_chikou = dframe['ICH_SSA'].iloc[-27]
            ssb_chikou = dframe['ICH_SSB'].iloc[-27]
            # print("tenkan_chikou", tenkan_chikou)
            # print("kijun_chikou", kijun_chikou)
            # print("ssa_chikou", ssa_chikou)
            # print("ssb_chikou", ssb_chikou)

            if check_timeframe(symbol, tf):
                print(symbol, tf, "Validated", "current price", price_close, "at", str(datetime.now()))

            if getting_over_the_cloud is True:
                condition = (ssb > ssa and price_open < ssb and price_close > ssb) \
                            or (ssa > ssb and price_open < ssa and price_close > ssa)
            elif getting_under_the_cloud is True:
                condition = (ssb > ssa and price_open > ssa and price_close < ssa) \
                            or (ssa > ssb and price_open > ssb and price_close < ssb)
            elif has_got_over_the_cloud is True:
                condition = ( (ssb > ssa and dframe['open'].iloc[-3] < dframe['ICH_SSB'].iloc[-3] \
                    and dframe['close'].iloc[-3] > dframe['ICH_SSB'].iloc[-3] \
                    and dframe['open'].iloc[-2] > dframe['ICH_SSB'].iloc[-2] \
                    and dframe['close'].iloc[-2] > dframe['ICH_SSB'].iloc[-2] \
                    and dframe['open'].iloc[-1] > dframe['ICH_SSB'].iloc[-1] \
                    and dframe['close'].iloc[-1] > dframe['ICH_SSB'].iloc[-1]) or \
                    (ssa > ssb and dframe['open'].iloc[-3] < dframe['ICH_SSA'].iloc[-3] \
                    and dframe['close'].iloc[-3] > dframe['ICH_SSA'].iloc[-3] \
                    and dframe['open'].iloc[-2] > dframe['ICH_SSA'].iloc[-2] \
                    and dframe['close'].iloc[-2] > dframe['ICH_SSA'].iloc[-2] \
                    and dframe['open'].iloc[-1] > dframe['ICH_SSA'].iloc[-1] \
                    and dframe['close'].iloc[-1] > dframe['ICH_SSA'].iloc[-1]) ) \
                    #and dframe['close'].iloc[-1] > dframe['open'].iloc[-1]
            elif getting_over_the_kijun is True:
                condition = (price_open < kijun and price_close > kijun)
            elif getting_under_the_kijun is True:
                condition = (price_open > kijun and price_close < kijun)
            elif has_got_over_the_kijun is True:
                condition = (dframe['open'].iloc[-3] < dframe['ICH_KS'].iloc[-3] and \
                    dframe['close'].iloc[-3] > dframe['ICH_KS'].iloc[-3] and \
                    dframe['open'].iloc[-2] > dframe['ICH_KS'].iloc[-2] and \
                    dframe['close'].iloc[-2] > dframe['ICH_KS'].iloc[-2]) and \
                    dframe['open'].iloc[-1] > dframe['ICH_KS'].iloc[-1] and \
                    dframe['close'].iloc[-1] > dframe['ICH_KS'].iloc[-1]
                #condition = (dframe['open'].iloc[-2] < dframe['ICH_KS'].iloc[-2] and \
                #    dframe['close'].iloc[-2] > dframe['ICH_KS'].iloc[-2] and \
                #    dframe['open'].iloc[-1] > dframe['ICH_KS'].iloc[-1] and \
                #    dframe['close'].iloc[-1] > dframe['ICH_KS'].iloc[-1])
            elif getting_over_the_tenkan is True:
                condition = (price_open < tenkan and price_close > tenkan)
            elif getting_under_the_tenkan is True:
                condition = (price_open > tenkan and price_close < tenkan)
            elif is_over_the_cloud is True:
                condition = (price_open > ssa and price_close > ssa and price_open > ssb and price_close > ssb)
            elif is_under_the_cloud is True:
                condition = (price_open < ssa and price_close < ssa and price_open < ssb and price_close < ssb)
            else:
                condition = price_close > ssa and price_close > ssb and price_close > tenkan and price_close > kijun \
                            and chikou > ssa_chikou and chikou > ssb_chikou and chikou > price_high_chikou \
                            and chikou > tenkan_chikou and chikou > kijun_chikou

            if chikou_validated_up is True:
                condition = condition and (chikou > ssa_chikou and chikou > ssb_chikou and chikou > price_high_chikou and chikou > tenkan_chikou and chikou > kijun_chikou)

            if chikou_validated_down is True:
                condition = condition and (chikou < ssa_chikou and chikou < ssb_chikou and chikou < price_low_chikou and chikou < tenkan_chikou and chikou < kijun_chikou)

            if price_validated_up is True:
                condition = condition and (price_close > ssa and price_close > ssb and price_close > tenkan and price_close > kijun and price_close > price_open)

            if price_validated_down is True:
                condition = condition and (price_close < ssa and price_close < ssb and price_close < tenkan and price_close < kijun and price_close < price_open)


        except:
            #print(tf, symbol, sys.exc_info())  # for getting more details remove this line and add line exit(-1) just before the "pass" function
            log_to_errors(str(datetime.now()) + " " + tf + " " + symbol + " " + str(sys.exc_info()))
            binary_result += "0"
            pass

        if delay_request > 0:
            if debug_delays:
                print("applying delay_request of", delay_thread, "s after request on timeframe", tf, symbol)
            time.sleep(delay_request)




threadLimiter = threading.BoundedSemaphore()


def scan_one(symbol, type_of_asset, exchange_id):
    global threadLimiter
    threadLimiter.acquire()
    try:
        execute_code(symbol, type_of_asset, exchange_id)
    finally:
        threadLimiter.release()




def main_thread():
    maxthreads = 1
    if exchange.id.lower() == "binance":
        maxthreads = 50
        print("setting maxthreads =", maxthreads, "for", exchange.id)
        delay_thread = 0  # 0.1  # delay between each start of a thread (in seconds, eg. 0.5 for 500ms, 1 for 1s...)
        delay_request = 0  # 0.250 # delay between each request inside of a thread
        print("setting delay_thread =", delay_thread, "for", exchange.id)
        print("setting delay_request =", delay_request, "for", exchange.id)
    elif exchange.id.lower() == "ftx":
        maxthreads = 100
        print("setting maxthreads =", maxthreads, "for", exchange.id)
        delay_thread = 0.1  # delay between each start of a thread (in seconds, eg. 0.5 for 500ms, 1 for 1s...)
        delay_request = 0.250  # delay between each request inside of a thread
        print("setting delay_thread =", delay_thread, "for", exchange.id)
        print("setting delay_request =", delay_request, "for", exchange.id)
    elif exchange.id.lower() == "gateio":
        maxthreads = 100
        print("setting maxthreads =", maxthreads, "for", exchange.id)
        delay_thread = 0.1  # delay between each start of a thread (in seconds, eg. 0.5 for 500ms, 1 for 1s...)
        delay_request = 0.250  # delay between each request inside of a thread
        print("setting delay_thread =", delay_thread, "for", exchange.id)
        print("setting delay_request =", delay_request, "for", exchange.id)
    elif exchange.id.lower() == "bitforex":
        maxthreads = 1
        print("setting maxthreads =", maxthreads, "for", exchange.id)
        delay_thread = 1  # delay between each start of a thread (in seconds, eg. 0.5 for 500ms, 1 for 1s...)
        delay_request = 1  # delay between each request inside of a thread
        print("setting delay_thread =", delay_thread, "for", exchange.id)
        print("setting delay_request =", delay_request, "for", exchange.id)
    else:
        maxthreads = 25
        delay_thread = 0
        delay_request = 0
        print("setting default maxthreads =", maxthreads, "for", exchange.id)
        print("setting default delay_thread =", delay_thread, "for", exchange.id)
        print("setting default delay_request =", delay_request, "for", exchange.id)

    delete_results_log()
    delete_results_evol_log()
    log_to_results("Scan results at : " + str(datetime.now()))

    threadLimiter = threading.BoundedSemaphore(maxthreads)
    # print(threadLimiter)

    ok = False
    while ok is False:
        try:
            markets = exchange.fetch_markets()
            ok = True
            print("markets data obtained successfully")
        except (ccxt.ExchangeError, ccxt.NetworkError, ccxt.DDoSProtection):
            print("Exchange seems not available (maybe too many requests). Please wait and try again.")
            # exit(-10002)
            if retry is False:
                print("will not retry.")
                exit(-777)
            else:
                print("will retry in 5 sec")
                time.sleep(5)
        except:
            print(sys.exc_info())
            exit(-778)

    threads = []

    # print(markets)
    stop = True
    if loop_scan:
        stop = False

    while True:
        for oneline in markets:
            symbol = oneline['id']
            active = oneline['active']
            type_of_asset = oneline['type']
            exchange_id = exchange.id.lower()
            base = oneline['base']  # eg. BTC/USDT => base = BTC
            quote = oneline['quote']  # eg. BTC/USDT => quote = USDT
            # print(symbol, "base", base, "quote", quote)

            # print("eval", eval("exchange_id == 'ftx'"))

            # this condition could be commented (and then more assets would be scanned)
            if exchange_id == "ftx":
                if symbol.endswith('HEDGE/USD') or symbol.endswith('CUSDT/USDT') or symbol.endswith('BEAR/USDT') \
                        or symbol.endswith('BEAR/USD') or symbol.endswith('BULL/USDT') or symbol.endswith('BULL/USD') \
                        or symbol.endswith('HALF/USD') or symbol.endswith('HALF/USDT') or symbol.endswith('SHIT/USDT') \
                        or symbol.endswith('SHIT/USD') or symbol.endswith('BEAR2021/USDT') or symbol.endswith(
                    'BEAR2021/USD') \
                        or symbol.endswith('BVOL/USDT') or symbol.endswith('BVOL/USD'):
                    continue

            condition_ok = active and filter_assets in symbol
            if filter_assets.startswith("*"):
                new_filter_assets = filter_assets.replace("*", "")
                new_filter_assets = new_filter_assets.upper()
                condition_ok = active and symbol.endswith(new_filter_assets)
            elif filter_assets.endswith("*"):
                new_filter_assets = filter_assets.replace("*", "")
                new_filter_assets = new_filter_assets.upper()
                condition_ok = active and symbol.startswith(new_filter_assets)

            if condition_ok:  # and ((symbol.endswith("USDT")) or (symbol.endswith("USD"))):  # == symbol: #'BTCUSDT':
                try:
                    t = threading.Thread(target=scan_one, args=(symbol, type_of_asset, exchange_id))
                    threads.append(t)
                    t.start()
                    #print("thread started for", symbol)
                    if delay_thread > 0:
                        if debug_delays:
                            print("applying delay_thread of", delay_thread, "s before next thread start")
                        time.sleep(delay_thread)

                except:
                    pass

        start_time = time.time()

        for tt in threads:
            tt.join()

        end_time = time.time()

        print("--- %s seconds ---" % (end_time - start_time))


        if stop is True:
            break


mainThread = threading.Thread(target=main_thread, args=())
mainThread.start()
