import os
from datetime import datetime
from datetime import timedelta

import ftx
import pandas as pd
import requests
import threading
import time
import ta
import math
import glob
from enum import Enum

# import numpy as np

client = ftx.FtxClient(
    api_key='',
    api_secret='',
    subaccount_name=''
)

# result = client.get_balances()
# print(result)

if os.path.exists("results.txt"):
    os.remove("results.txt")

if os.path.exists("errors.txt"):
    os.remove("errors.txt")

for fg in glob.glob("CS_*.txt"):
    os.remove(fg)

list_results = []
results_count = 0

stop_thread = False


def my_thread(name):
    global client, list_results, results_count
    while not stop_thread:

        f = open("results.txt", "a")
        new_results_found = False

        markets = requests.get('https://ftx.com/api/markets').json()
        df = pd.DataFrame(markets['result'])
        df.set_index('name')
        for index, row in df.iterrows():
            symbol = row['name']
            symbol_type = row['type']

            # filtering symbols to scan here
            if not (symbol.endswith("/USD")) and not (symbol.endswith('/USDT')):
                continue

            symbols_to_exclude = ["BEAR/USD", "BULL/USD", "HEDGE/USD", "HALF/USD", "BEAR/USDT", "BULL/USDT", "HEDGE/USDT", "HALF/USDT", "-PERP", "-1231", "BEAR2021/USD",
                                  "SHIT/USD", "VOL/USD", "VOL/USDT"]

            go_to_next_symbol = False

            for ste in symbols_to_exclude:
                if symbol.endswith(ste):
                    go_to_next_symbol = True

            if go_to_next_symbol:
                continue

            print("scanning", symbol, symbol_type)

            # if symbol.endswith("BEAR/USD") or symbol.endswith("BULL/USD") or symbol.endswith("HEDGE/USD") or symbol.endswith():
            #     continue

            data = client.get_historical_data(
                market_name=symbol,
                resolution=60 * 15,  # 60min * 60sec = 3600 sec
                limit=10000,
                start_time=float(round(time.time())) - 3 * 15 * 3600,
                # 1000*3600 for resolution=3600*24 (daily) # 3600*3 for resolution=60*5 (5min) # 3600*3*15 for 60*15 # 3600 * 3 * 15 * 2 for 60*60
                end_time=float(round(time.time())))

            dframe = pd.DataFrame(data)

            # dframe['time'] = pd.to_datetime(dframe['time'], unit='ms')

            # print(dframe)
            try:
                dframe['ICH_SSA'] = ta.trend.ichimoku_a(dframe['high'], dframe['low'], window1=9, window2=26).shift(26)
                dframe['ICH_SSB'] = ta.trend.ichimoku_b(dframe['high'], dframe['low'], window2=26, window3=52).shift(26)
                dframe['ICH_KS'] = ta.trend.ichimoku_base_line(dframe['high'], dframe['low'])
                dframe['ICH_TS'] = ta.trend.ichimoku_conversion_line(dframe['high'], dframe['low'])
                dframe['ICH_CS'] = dframe['close'].shift(-26)

            except KeyError as err:
                print(err)
                continue

            for indexdf, rowdf in dframe.iterrows():
                openp = rowdf['open']
                high = rowdf['high']
                low = rowdf['low']
                close = rowdf['close']
                ssa = rowdf['ICH_SSA']
                ssb = rowdf['ICH_SSB']
                ks = rowdf['ICH_KS']
                ts = rowdf['ICH_TS']
                # cs = rowdf['ICH_CS']
                try:
                    cs = dframe['ICH_CS'].iloc[-26 - 1]  # chikou span concernant bougie n en cours
                    cs2 = dframe['ICH_CS'].iloc[-26 - 2]  # chikou span concernant bougie n-1
                    ssbchikou = dframe['ICH_SSB'].iloc[-26 - 1 + 2]
                    ssbchikou2 = dframe['ICH_SSB'].iloc[-26 - 2 + 2]
                    ssbchikou3 = dframe['ICH_SSB'].iloc[-26 - 3 + 2]
                    closechikou = dframe['close'].iloc[-26]
                    closechikou2 = dframe['close'].iloc[-26 - 1]
                    kijunchikou = dframe['ICH_KS'].iloc[-26 - 1 + 1]
                    kijunchikou2 = dframe['ICH_KS'].iloc[-26 - 2 + 1]
                    kijunchikou3 = dframe['ICH_KS'].iloc[-26 - 3 + 1]
                    tenkanchikou = dframe['ICH_TS'].iloc[-26 - 1 + 1]
                    tenkanchikou2 = dframe['ICH_TS'].iloc[-26 - 2 + 1]
                    tenkanchikou3 = dframe['ICH_TS'].iloc[-26 - 3 + 1]
                    ssachikou = dframe['ICH_SSA'].iloc[-26 - 1 + 2]
                    ssachikou2 = dframe['ICH_SSA'].iloc[-26 - 2 + 2]
                    ssachikou3 = dframe['ICH_SSA'].iloc[-26 - 3 + 2]

                except IndexError as error:
                    print(symbol + " EXCEPTION " + str(error))
                    fe = open("errors.txt", "a")
                    fe.write(symbol + " EXCEPTION " + str(error) + '\n')
                    fe.close()
                    # quit(0)
                    continue

                timestamp = pd.to_datetime(rowdf['time'], unit='ms')

                error_nan_values = False
                # To check the values of Ichimoku data (use TradingView with Ichimoku Cloud to compare them)
                # print(str(timestamp) + " " + symbol + " closecs=" + str(closechikou) + " closecs2=" + str(closechikou2) + " CS=" + str(cs) + " CS2=" + str(cs2) + " SSBCS=" + str(ssbchikou) + " SSBCS2=" + str(ssbchikou2) + " SSBCS3=" + str(ssbchikou3) + " KSCS=" + str(kijunchikou)+ " KSCS2=" + str(kijunchikou2)+ " KSCS3=" + str(kijunchikou3) + " TSCS=" + str(tenkanchikou)+ " TSCS2=" + str(tenkanchikou2)+ " TSCS3=" + str(tenkanchikou3) + " SSACS=" + str(ssachikou) + " SSACS2=" + str(ssachikou2) + " SSACS3=" + str(ssachikou3))
                if math.isnan(closechikou) or math.isnan(closechikou2) or math.isnan(cs) or math.isnan(cs2) or math.isnan(ssbchikou) or math.isnan(ssbchikou2) or math.isnan(
                        ssbchikou3) or math.isnan(kijunchikou) or math.isnan(kijunchikou2) or math.isnan(kijunchikou3) or math.isnan(tenkanchikou) or math.isnan(
                    tenkanchikou2) or math.isnan(tenkanchikou3) or math.isnan(ssachikou) or math.isnan(ssbchikou2) or math.isnan(ssachikou3):
                    print(symbol + " THERE ARE NAN VALUES IN ICHIMOKU DATA")
                    fe = open("errors.txt", "a")
                    fe.write(symbol + " THERE ARE NAN VALUES IN ICHIMOKU DATA" + '\n')
                    fe.close()
                    error_nan_values = True
                    # quit(0)

                if error_nan_values:
                    continue

                filename = "CS_" + symbol.replace('/', '_') + ".txt"
                if os.path.exists(filename):
                    os.remove(filename)

                # now_cs = datetime.now() - timedelta(hours=4 * 26)
                # # print("now_cs=" + str(now_cs))
                # # quit(0)
                # if timestamp.year == now_cs.year and timestamp.month == now_cs.year and timestamp.day == now_cs.day and timestamp.hour == now_cs.hour:
                #     print(str(cs))

                data_hour = timestamp.hour
                data_day = timestamp.day
                data_month = timestamp.month
                data_year = timestamp.year

                now = datetime.now() - timedelta(hours=1)
                now_hour = now.hour
                now_day = now.day
                now_month = now.month
                now_year = now.year

                # if math.isnan(ssa):
                #     print(symbol, "ssa is null")
                #
                # if math.isnan(ssb):
                #     print(symbol, "ssb is null")

                evol = round(((close - openp) / openp) * 100, 4)

                scan = True

                if scan:
                    if data_day == now_day and data_month == now_month and data_year == now_year and data_hour >= now_hour:  # remove the last condition for scanning in daily timeframe (60*60*24)
                        # if openp < ssb < close or openp > ssb and close > ssb:
                        # if openp > ssb and close > ssb and close > openp and openp > ssa and close > ssa and openp > ks and openp > ts and close > ks and close > ts:
                        if openp < close and close / openp > 1.015:
                            csresults = ""
                            if cs > ssbchikou:
                                csresults += "* CS > SSBCHIKOU - "
                            if cs > ssachikou:
                                csresults += "* CS > SSACHIKOU - "
                            if cs > kijunchikou:
                                csresults += "* CS > KSCHIKOU - "
                            if cs > tenkanchikou:
                                csresults += "* CS > TSCHIKOU - "
                            if cs > closechikou:
                                csresults += "* CS > CLOSECHIKOU"
                            # if csresults != "":
                            #     print(csresults)
                            #     fr = open("results.txt", "a")
                            #     fr.write(csresults + '\n')
                            #     fr.close()

                            # print(timestamp, symbol, "O", openp, "H", high, "L", low, "C", close, "SSA", ssa, "SSB", ssb, "KS", ks, "TS", ts, "CS", cs, "EVOL%", evol)
                            # print("")
                            strn = str(timestamp) + " " + symbol + " SSA=" + str(ssa) + " SSB=" + str(
                                ssb) + " KS=" + str(ks) + " TS=" + str(ts) + " O=" + str(openp) + " H=" + str(high) + " L=" + str(
                                low)  # + " C=" + str(close) + " CS=" + str(cs) + " EVOL%=" + str(evol)

                            if not (strn in list_results):
                                if not new_results_found:
                                    new_results_found = True
                                results_count = results_count + 1
                                list_results.append(strn)
                                print(csresults)
                                print(str(results_count) + " " + strn + " C=" + str(close) + " CS=" + str(cs) + " EVOL%=" + str(evol) + "\n")

                                fr = open("results.txt", "a")
                                fr.write(csresults + '\n')
                                fr.write(strn + " C=" + str(close) + " CS=" + str(cs) + " EVOL%=" + str(evol) + '\n\n')
                                fr.close()

                else:
                    if data_day == now_day and data_month == now_month and data_year == now_year and (data_hour >= now_hour):
                        print(timestamp, symbol, "O", openp, "H", high, "L", low, "C", close, "SSA", ssa, "SSB", ssb, "KS", ks, "TS", ts, "CS", cs)
                        strn = str(timestamp) + " " + symbol + " O=" + str(openp) + " H=" + str(high) + " L=" + str(low) + " C=" + str(close) + " SSA=" + str(ssa) + " SSB=" + str(
                            ssb) + " KS=" + str(ks) + " TS=" + str(ts) + " CS=" + str(cs) + " EVOL%" + str(evol)
                        fr = open("results.txt", "a")
                        fr.write(strn + '\n')
                        fr.close()

        if new_results_found:
            fr = open("results.txt", "a")
            fr.write(100 * '*' + '\n')
            fr.close()


x = threading.Thread(target=my_thread, args=(1,))
x.start()
