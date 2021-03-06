# functional but always adding new features

"""
THIS PROGRAM IS MEANT TO BE RUN AT THE END OF A TRADING DAY
DOESNT REALLY MATTER HOW LONG IT TAKES, SPEED ISN'T IMPORTANT

ALSO AS I HAVE JUST FIGURED OUT, THE VALUES FOR LOSSES AND GAINS ARE WONKY IF THERE IS A NET
POSITIVE POSITION BY THE END OF THE TRADING DAY
"""
import alpaca_trade_api as trade_api
from pandas import DataFrame
import datetime as dt
import pandas as pd
import openpyxl
import win32com.client as win32
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import time


def data_to_excel(metrics):
    book = openpyxl.load_workbook('Portfolio Data.xlsx')
    writer = pd.ExcelWriter('Portfolio Data.xlsx', engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    metrics.to_excel(writer, sheet_name=sheet_name)
    try:
        sheet = book['Sheet']
        book.remove(sheet)
        book.save('Portfolio Data.xlsx')
    except KeyError:
        pass
    writer.save()


def formatting_excel(name):
    excel = win32.Dispatch('Excel.Application')
    excel.Visible = 1
    wkb = excel.Workbooks.Open(r"C:\Users\fabio\PycharmProjects\AlgoTrader\Portfolio Data.xlsx")
    ws = wkb.Worksheets(name)
    ws.Columns.AutoFit()
    wkb.Save()
    excel.Application.Quit()


def webscraping(tickers):
    try:
        bond_url = 'http://www.marketwatch.com/investing/bond/tmubmusd01m?countrycode=bx'
        driver.get(bond_url)
        html = driver.execute_script('return document.body.innerHTML;')
        soup = BeautifulSoup(html, 'lxml')
        try:
            bondlist = [entry.text for entry in
                        soup.find_all('bg-quote', {'class': 'value', 'field': 'Last'})]
            risk_free_rate = float(bondlist[0])
            print("1 month risk-free-rate", str(risk_free_rate) + str('%'))
        except IndexError:
            print("Failed to fetch 1-Month T-bond Yield! Setting to default value (0.01)")
            risk_free_rate = 0.01

        for stock in tickers:
            quote = {}
            stock_url = 'https://finance.yahoo.com/quote/' + stock + '?p=' + stock
            driver.get(stock_url)
            html = driver.execute_script('return document.body.innerHTML;')
            soup = BeautifulSoup(html, 'lxml')
            beta_metric = [entry.text for entry in soup.find_all('span', {'data-reactid': '144'})]
            return_pct = [entry.text for entry in soup.find_all('span', {'data-reactid': '51'})]
            delimiter1 = '('
            delimiter2 = ')'
            formatted_return = str(return_pct[0])
            rt = formatted_return[formatted_return.find(delimiter1) + 1: formatted_return.find(delimiter2)]
            return_string = rt.split("%")[0]
            returns = float(return_string)
            print(stock, returns)
            quote['stock'] = stock
            quote['beta'] = beta_metric[0]
            quote['returns'] = round(returns, 4)
            quote_data[stock] = quote
        # spy
        spy_url = 'https://finance.yahoo.com/quote/SPY?p=SPY'
        driver.get(spy_url)
        html = driver.execute_script('return document.body.innerHTML;')
        soup = BeautifulSoup(html, 'lxml')
        spy_returns_pct = [entry.text for entry in soup.find_all('span', {'data-reactid': '51'})]
        delimiter1 = '('
        delimiter2 = ')'
        formatted_return = str(spy_returns_pct[0])
        rt = formatted_return[formatted_return.find(delimiter1) + 1: formatted_return.find(delimiter2)]
        return_string = rt.split("%")[0]
        spy_returns = float(return_string)
        return spy_returns, risk_free_rate
    except Exception as e:
        print(e)
    finally:
        driver.quit()


def purchasing_filter(activities_df):
    # filtering out bull side long purchases
    long_purchases_df = activities_df.loc[(activities_df['side'] == 'buy') & (activities_df['cumulative_sum'] > 0)]
    total_long_purchases = round(long_purchases_df['net_trade'].sum(), 2)
    print("Gross cost of long positions:", total_long_purchases)

    # filtering out bear side 'buy to cover' purchases
    short_purchases_df = activities_df.loc[(activities_df['side'] == 'buy') & (activities_df['cumulative_sum'] <= 0)]
    total_short_purchases = round(short_purchases_df['net_trade'].sum(), 2)
    print("Gross cost of short positions:", total_short_purchases)

    # filtering bull side long sales
    long_sales_df = activities_df.loc[activities_df['side'] == 'sell']
    total_long_sells = round(long_sales_df['net_trade'].sum(), 2)
    print("Gross profit of long positions:", total_long_sells)

    # filtering bear side short purchases
    short_sales_df = activities_df.loc[activities_df['side'] == 'sell_short']
    total_short_sells = round(short_sales_df['net_trade'].sum(), 2)
    print("Gross profit of short positions:", total_short_sells)

    long_buy_df = long_purchases_df.sort_values(['symbol', 'transaction_time'])
    lb_df = pd.DataFrame(long_buy_df)
    lb_df.reset_index(drop=True, inplace=True)

    long_sales_df = long_sales_df.sort_values(['symbol', 'transaction_time'])
    ls_df = pd.DataFrame(long_sales_df)
    ls_df.reset_index(drop=True, inplace=True)

    short_buys_df = short_purchases_df.sort_values(['symbol', 'transaction_time'])
    sb_df = pd.DataFrame(short_buys_df)
    sb_df.reset_index(drop=True, inplace=True)

    short_sells_df = short_sales_df.sort_values(['symbol', 'transaction_time'])
    ss_df = pd.DataFrame(short_sells_df)
    ss_df.reset_index(drop=True, inplace=True)
    return lb_df, ls_df, sb_df, ss_df


def order_settlement():
    current_buy_pos = 0
    current_sell_pos = 0
    ###################################################################################################################
    for place, it in enumerate(short_buy_order_book.copy(), start=current_buy_pos):
        try:
            place = current_buy_pos
            o = 1
            buy_qty = short_buy_order_book[current_buy_pos][2]
            buy_value = short_buy_order_book[current_buy_pos][3]
            if short_buy_order_book[current_buy_pos][1] == 'partial_fill':
                while True:
                    if short_buy_order_book[current_buy_pos + o][1] == 'partial_fill':
                        buy_qty += short_buy_order_book[current_buy_pos + o][2]
                        buy_value += short_buy_order_book[current_buy_pos + o][3]
                        o += 1
                    else:
                        buy_qty += short_buy_order_book[current_buy_pos + o][2]
                        buy_value += short_buy_order_book[current_buy_pos + o][3]
                        short_buy_order_book[current_buy_pos + o][2] = buy_qty
                        short_buy_order_book[current_buy_pos + o][3] = round(buy_value, 2)
                        for j in range(o):
                            del short_buy_order_book[current_buy_pos + j]
                        break
            current_buy_pos += o
            place += o
        except KeyError:
            pass
    print(len(short_buy_order_book), short_buy_order_book)

    for place, it in enumerate(short_sell_order_book.copy(), start=current_sell_pos):
        try:
            place = current_sell_pos
            o = 1
            buy_qty = short_sell_order_book[current_sell_pos][2]
            buy_value = short_sell_order_book[current_sell_pos][3]
            if short_sell_order_book[current_sell_pos][1] == 'partial_fill':
                while True:
                    if short_sell_order_book[current_sell_pos + o][1] == 'partial_fill':
                        buy_qty += short_sell_order_book[current_sell_pos + o][2]
                        buy_value += short_sell_order_book[current_sell_pos + o][3]
                        o += 1
                    else:
                        buy_qty += short_sell_order_book[current_sell_pos + o][2]
                        buy_value += short_sell_order_book[current_sell_pos + o][3]
                        short_sell_order_book[current_sell_pos + o][2] = buy_qty
                        short_sell_order_book[current_sell_pos + o][3] = round(buy_value, 2)
                        for j in range(o):
                            del short_sell_order_book[current_sell_pos + j]
                        break
            current_sell_pos += o
            place += o
        except KeyError:
            pass
    print(len(short_sell_order_book), short_sell_order_book)

    current_buy_pos = 0
    current_sell_pos = 0
    for place, it in enumerate(buy_order_book.copy(), start=current_buy_pos):
        try:
            place = current_buy_pos
            o = 1
            buy_qty = buy_order_book[current_buy_pos][2]
            buy_value = buy_order_book[current_buy_pos][3]
            if buy_order_book[current_buy_pos][1] == 'partial_fill':
                while True:
                    if buy_order_book[current_buy_pos + o][1] == 'partial_fill':
                        buy_qty += buy_order_book[current_buy_pos + o][2]
                        buy_value += buy_order_book[current_buy_pos + o][3]
                        o += 1
                    else:
                        buy_qty += buy_order_book[current_buy_pos + o][2]
                        buy_value += buy_order_book[current_buy_pos + o][3]
                        buy_order_book[current_buy_pos + o][2] = buy_qty
                        buy_order_book[current_buy_pos + o][3] = round(buy_value, 2)
                        for h in range(o):
                            del buy_order_book[current_buy_pos + h]
                        break
            current_buy_pos += o
            place += o
        except KeyError:
            pass
    print(len(buy_order_book), buy_order_book)

    for place, it in enumerate(sell_order_book.copy(), start=current_sell_pos):
        try:
            place = current_sell_pos
            o = 1
            sell_qty = sell_order_book[current_sell_pos][2]
            sell_value = sell_order_book[current_sell_pos][3]
            if sell_order_book[current_sell_pos][1] == 'partial_fill':
                while True:
                    if sell_order_book[current_sell_pos + o][1] == 'partial_fill':
                        sell_qty += sell_order_book[current_sell_pos + o][2]
                        sell_value += sell_order_book[current_sell_pos + o][3]
                        o += 1
                    else:
                        sell_qty += sell_order_book[current_sell_pos + o][2]
                        sell_value += sell_order_book[current_sell_pos + o][3]
                        sell_order_book[current_sell_pos + o][2] = sell_qty
                        sell_order_book[current_sell_pos + o][3] = round(sell_value, 2)
                        for p in range(o):
                            del sell_order_book[current_sell_pos + p]
                        break
            current_sell_pos += o
            place += o
        except KeyError:
            pass
    print(len(sell_order_book), sell_order_book)


def trade_book_settlement():
    trade_book = {}
    short_trade_book = {}
    short_order_time_held = {}
    long_order_time_held = {}
    ####################################################################################################################
    # adding to respective trade books
    current_buy_pos = 0
    current_sell_pos = 0
    short_trade_ledger_position = 0

    while len(short_buy_order_book) > 0:
        for pos, k in enumerate(short_buy_order_book.copy(), start=current_buy_pos):
            d1 = dt.datetime.strptime(short_buy_order_book[current_buy_pos][0], "%Y-%m-%dT%H:%M:%S.%fZ")
            d2 = dt.datetime.strptime(short_sell_order_book[current_sell_pos][0], "%Y-%m-%dT%H:%M:%S.%fZ")
            elapsed_time = (d1 - d2).total_seconds()

            if short_buy_order_book[current_buy_pos][5] == short_sell_order_book[current_sell_pos][5]:
                if short_buy_order_book[current_buy_pos][2] == short_sell_order_book[current_sell_pos][2]:
                    short_trade_book[short_trade_ledger_position] = round(short_buy_order_book[current_buy_pos][3] +
                                                                          short_sell_order_book[current_sell_pos][3], 2)
                    short_order_time_held[short_trade_ledger_position] = (elapsed_time,
                                                                          short_buy_order_book[current_buy_pos][2])
                    del short_buy_order_book[current_buy_pos], short_sell_order_book[current_sell_pos]

                else:
                    while True:
                        bought_share_value = round(
                            short_buy_order_book[current_buy_pos][3] / short_buy_order_book[current_buy_pos][2], 2)
                        sold_share_value = round(
                            short_sell_order_book[current_sell_pos][3] / short_sell_order_book[current_sell_pos][2], 2)
                        buy_quantity = short_buy_order_book[current_buy_pos][2]
                        sell_quantity = short_sell_order_book[current_sell_pos][2]
                        buy_val = short_buy_order_book[current_buy_pos][3]
                        sell_val = short_sell_order_book[current_sell_pos][3]

                        if buy_quantity > sell_quantity:
                            value_of_shares_sold = bought_share_value * sell_quantity
                            short_trade_book[short_trade_ledger_position] = round(value_of_shares_sold + sell_val, 2)
                            short_buy_order_book[current_buy_pos][2] -= sell_quantity
                            short_buy_order_book[current_buy_pos][3] = round(buy_val - value_of_shares_sold, 2)
                            short_buy_order_book[current_buy_pos][4] -= sell_quantity
                            short_order_time_held[short_trade_ledger_position] = (elapsed_time, sell_quantity)
                            del short_sell_order_book[current_sell_pos]
                            break

                        if buy_quantity < sell_quantity:
                            value_of_shares_sold = sold_share_value * buy_quantity
                            short_sell_order_book[current_sell_pos][2] -= buy_quantity
                            short_sell_order_book[current_sell_pos][3] = round(sell_val - value_of_shares_sold, 2)
                            short_trade_book[short_trade_ledger_position] = round(value_of_shares_sold + buy_val, 2)
                            short_order_time_held[short_trade_ledger_position] = (elapsed_time, buy_quantity)
                            del short_buy_order_book[current_buy_pos]
                        break
            else:
                price_per_share = round(short_sell_order_book[current_sell_pos][3] /
                                        short_sell_order_book[current_sell_pos][2], 2)
                print("There is a net short position of {} shares on {} at a price of ${} per share".format(
                    short_sell_order_book[current_sell_pos][2], short_sell_order_book[current_sell_pos][5],
                    price_per_share))
                del short_sell_order_book[current_sell_pos]

            if len(short_buy_order_book) > 0:
                current_buy_pos = list(short_buy_order_book)[0]
                current_sell_pos = list(short_sell_order_book)[0]
                short_trade_ledger_position += 1

    current_buy_pos = 0
    current_sell_pos = 0
    trade_ledger_position = 0

    while len(buy_order_book) > 0:
        for pos, k in enumerate(buy_order_book.copy(), start=current_buy_pos):
            d1 = dt.datetime.strptime(buy_order_book[current_buy_pos][0], "%Y-%m-%dT%H:%M:%S.%fZ")
            d2 = dt.datetime.strptime(sell_order_book[current_sell_pos][0], "%Y-%m-%dT%H:%M:%S.%fZ")
            elapsed_time = (d2 - d1).total_seconds()
            # check if the symbols match

            if buy_order_book[current_buy_pos][5] == sell_order_book[current_sell_pos][5]:
                if buy_order_book[current_buy_pos][2] == sell_order_book[current_sell_pos][2]:
                    trade_book[trade_ledger_position] = round(
                        buy_order_book[current_buy_pos][3] + sell_order_book[current_sell_pos][3], 2)
                    long_order_time_held[trade_ledger_position] = (elapsed_time, buy_order_book[current_buy_pos][2])
                    del buy_order_book[current_buy_pos], sell_order_book[current_sell_pos]

                else:
                    while True:
                        bought_share_value = round(buy_order_book[current_buy_pos][3] / buy_order_book[current_buy_pos][2],
                                                   2)
                        sold_share_value = round(
                            sell_order_book[current_sell_pos][3] / sell_order_book[current_sell_pos][2], 2)
                        buy_quantity = buy_order_book[current_buy_pos][2]
                        sell_quantity = sell_order_book[current_sell_pos][2]
                        buy_val = buy_order_book[current_buy_pos][3]
                        sell_val = sell_order_book[current_sell_pos][3]

                        if buy_quantity > sell_quantity:
                            value_of_shares_sold = bought_share_value * sell_quantity
                            trade_book[trade_ledger_position] = round(value_of_shares_sold + sell_val, 2)
                            buy_order_book[current_buy_pos][2] -= sell_quantity
                            buy_order_book[current_buy_pos][3] = round(buy_val - value_of_shares_sold, 2)
                            buy_order_book[current_buy_pos][4] -= sell_quantity
                            long_order_time_held[trade_ledger_position] = (elapsed_time, sell_quantity)
                            del sell_order_book[current_sell_pos]
                            break

                        if buy_quantity < sell_quantity:
                            value_of_shares_sold = sold_share_value * buy_quantity
                            sell_order_book[current_sell_pos][2] -= buy_quantity
                            sell_order_book[current_sell_pos][3] = round(sell_val - value_of_shares_sold, 2)
                            trade_book[trade_ledger_position] = round(value_of_shares_sold + buy_val, 2)
                            long_order_time_held[trade_ledger_position] = (elapsed_time, buy_quantity)
                            del buy_order_book[current_buy_pos]
                        break
            else:
                price_per_share = round(buy_order_book[current_buy_pos][3] / buy_order_book[current_buy_pos][2], 2)
                print("There is a net long position of {} shares on {} at a price of ${} per share".format(
                    buy_order_book[current_buy_pos][2], buy_order_book[current_buy_pos][5], price_per_share))
                del buy_order_book[current_buy_pos]

            if len(buy_order_book) > 0:
                current_buy_pos = list(buy_order_book)[0]
                current_sell_pos = list(sell_order_book)[0]
                trade_ledger_position += 1
    return short_trade_book, trade_book, short_order_time_held, long_order_time_held


if __name__ == '__main__':
    if not os.path.isfile(r"C:\Users\fabio\PycharmProjects\AlgoTrader\Portfolio Data.xlsx"):
        wb = openpyxl.Workbook()
        wb.save('Portfolio Data.xlsx')

    pd.options.mode.chained_assignment = None
    key = "PKCPC6RJ84BG84W3PB60"
    sec = "U1r9Z2QknL9FwAaTztfLl5g1DTxpa5m97qyWCGZ7"
    url = "https://paper-api.alpaca.markets"
    api = trade_api.REST(key, sec, url, api_version='v2')

    # Can also limit the results by date if desired.
    days = 1
    while True:
        try:
            spec_date = dt.datetime.today() - dt.timedelta(days=days)
            date = spec_date.strftime('%Y-%m-%d')
            activities = api.get_activities(activity_types='FILL', date=date)
            activities_df = pd.DataFrame([activity._raw for activity in activities])
            if not len(activities_df) > 50:
                raise Exception("Not enough trades to not be a test")
            else:
                print("Analyzing Portfolio Activities on {}".format(date))

            activities_df = activities_df.iloc[::-1]
            activities_df[['price', 'qty']] = activities_df[['price', 'qty']].apply(pd.to_numeric)
            activities_df['net_qty'] = np.where(activities_df.side == 'buy', activities_df.qty, -activities_df.qty)
            activities_df['net_trade'] = -activities_df.net_qty * activities_df.price
            activities_df['cumulative_sum'] = activities_df.groupby('symbol')['net_qty'].apply(lambda g: g.cumsum())
            break
        except Exception as e:
            days += 1

    activities_df.to_excel("Portfolio Activities.xlsx")

    ###################################################################################################################
    # Total Net Profit for Long and Short Trades
    long_buy_df, long_sell_df, short_buy_df, short_sell_df = purchasing_filter(activities_df)

    # we can make an order book that tracks each trade as it iterates down the list
    short_buy_order_book = {}
    for index, row in short_buy_df.iterrows():
        short_buy_order_book[index] = [row['transaction_time'], row['type'], row['qty'], round(row['net_trade'], 2),
                                       row['cumulative_sum'], row['symbol']]
    print("short buys", len(short_buy_order_book), short_buy_order_book)
    short_sell_order_book = {}
    for index, row in short_sell_df.iterrows():
        short_sell_order_book[index] = [row['transaction_time'], row['type'], row['qty'], round(row['net_trade'], 2),
                                        row['cumulative_sum'], row['symbol']]
    print("short sells", len(short_sell_order_book), short_sell_order_book)
    buy_order_book = {}
    for index, row in long_buy_df.iterrows():
        buy_order_book[index] = [row['transaction_time'], row['type'], row['qty'], round(row['net_trade'], 2),
                                 row['cumulative_sum'], row['symbol']]
    print("long buys", len(buy_order_book), buy_order_book)
    sell_order_book = {}
    for index, row in long_sell_df.iterrows():
        sell_order_book[index] = [row['transaction_time'], row['type'], row['qty'], round(row['net_trade'], 2),
                                  row['cumulative_sum'], row['symbol']]
    print("long sells", len(sell_order_book), sell_order_book)

    order_settlement()
    short_trades, long_trades, short_trade_time_ledger, long_trade_time_ledger = trade_book_settlement()
    ###################################################################################################################
    # finding average short trade held time
    print(short_trade_time_ledger)
    print(long_trade_time_ledger)
    short_hold_time = 0
    for position, item in enumerate(short_trade_time_ledger):
        try:
            short_hold_time += short_trade_time_ledger[position][0]
        except KeyError:
            pass
    average_short_trade_hold_time = round(short_hold_time / len(short_trade_time_ledger), 2)
    avg_total_trade_hold_time = average_short_trade_hold_time
    avg_short_trade_length = time.strftime("%M:%S", time.gmtime(average_short_trade_hold_time))
    print(avg_short_trade_length)

    long_hold_time = 0
    for position, item in enumerate(long_trade_time_ledger):
        long_hold_time += long_trade_time_ledger[position][0]
    average_long_trade_hold_time = round(long_hold_time / len(long_trade_time_ledger), 2)
    avg_total_trade_hold_time += average_long_trade_hold_time
    avg_long_trade_length = time.strftime("%M:%S", time.gmtime(average_long_trade_hold_time))
    print(avg_long_trade_length)
    # divide time held in seconds by time of avg trading day, 23400 seconds
    avg_total_trade_hold_time = time.strftime("%M:%S", time.gmtime((avg_total_trade_hold_time / 2)))
    ##################################################################
    total_gross_profit = 0
    total_gross_loss = 0
    short_gross_profit = 0
    short_gross_loss = 0
    net_short_profit = 0
    total_short_trades = 0
    short_winning_trades = 0
    short_even_trades = 0
    short_losing_trades = 0
    for i in range(len(short_trades)):
        try:
            if short_trades[i] > 0:
                short_winning_trades += 1
                short_gross_profit += short_trades[i]
                total_gross_profit += short_trades[i]
            elif short_trades[i] < 0:
                short_losing_trades += 1
                short_gross_loss += short_trades[i]
                total_gross_loss += short_trades[i]
            else:
                short_even_trades += 1
            total_short_trades += 1
            net_short_profit += short_trades[i]
        except KeyError:
            pass
    net_short_profit = round(net_short_profit, 2)
    print("Short-side net profit:", net_short_profit)
    print("Short-side profitable trades:", short_winning_trades)
    print("Short-side even trades:", short_even_trades)
    print("Short-side Losing trades:", short_losing_trades)
    print("Total short-side trades:", total_short_trades)

    # initialization of long variables
    long_gross_profit = 0
    long_gross_loss = 0
    net_long_profit = 0
    total_long_trades = 0
    long_winning_trades = 0
    long_even_trades = 0
    long_losing_trades = 0
    for i in range(len(long_trades)):
        if long_trades[i] > 0:
            long_winning_trades += 1
            long_gross_profit += long_trades[i]
            total_gross_profit += long_trades[i]
        elif long_trades[i] < 0:
            long_losing_trades += 1
            long_gross_loss += long_trades[i]
            total_gross_loss += long_trades[i]
        else:
            long_even_trades += 1
        total_long_trades += 1
        net_long_profit += long_trades[i]
    net_long_profit = round(net_long_profit, 2)
    print("\nLong-side net profit:", net_long_profit)
    print("Long-side profitable trades:", long_winning_trades)
    print("Long-side even trades:", long_even_trades)
    print("Long-side losing trades:", long_losing_trades)
    print("Total long-side trades", total_long_trades)

    avg_winning_trade = round((total_gross_profit / (long_winning_trades + short_winning_trades)), 2)
    avg_losing_trade = round((total_gross_loss / (total_long_trades + short_losing_trades)), 2)
    avg_long_winning_trade = round(long_gross_profit / long_winning_trades, 2)
    avg_long_losing_trade = round(long_gross_loss / long_losing_trades, 2)
    avg_short_winning_trade = round(short_gross_profit / short_winning_trades, 2)
    avg_short_losing_trade = round(short_gross_loss / short_losing_trades, 2)

    todayspandl = round(total_gross_profit + total_gross_loss, 2)
    total_gross_profit = round(total_gross_profit, 2)
    total_gross_loss = round(total_gross_loss, 2)
    print("\nProfit Metrics:")
    print("Gross Profit:", total_gross_profit)
    print("Average Winning Trade:", avg_winning_trade)
    print("Gross Loss:", total_gross_loss)
    print("Average Losing Trade:", avg_losing_trade)
    print("Total Net Profit:", todayspandl)

    # profit per symbol
    # handle having outstanding positions and remove the net positive positions so we can pin down the net gain
    # and loss for the stock on the trading day
    non_zero_trades = activities_df.groupby('symbol').filter(lambda trade: sum(trade.net_qty) != 0)
    print(non_zero_trades)
    # the last row of the dataframe will have potentially the outstanding position
    print(non_zero_trades.iloc[-1])
    while non_zero_trades.iloc[-1][13] != 0:
        print("Details on outstanding position(s):")
        print(non_zero_trades.iloc[-1])
        dfindex = non_zero_trades.index[-1]
        non_zero_trades = non_zero_trades.drop(dfindex)
        activities_df = activities_df.drop(dfindex)

    net_zero_trades = activities_df.groupby('symbol').filter(lambda trade: sum(trade.net_qty) == 0)
    trades = net_zero_trades.groupby('symbol').net_trade
    profit_per_symbol = net_zero_trades.groupby('symbol').net_trade.sum()
    print("Net Profit per stock:")
    print(profit_per_symbol)

    stock_tickers_involved = profit_per_symbol.index.tolist()
    print(stock_tickers_involved)
    #############################################################################
    pd.options.display.float_format = '{:.0f}'.format
    quote_data = {}
    for stock in stock_tickers_involved:
        quote_data[stock] = []
    #########################################################################################
    # for quick debugging
    driver = webdriver.Chrome(ChromeDriverManager().install())
    spyreturn, riskfreerate = webscraping(stock_tickers_involved)
    spyreturn = '{:.4f}'.format(spyreturn)
    spyreturn = float(spyreturn)
    print(quote_data)
    print(spyreturn)
    #############################################################################
    account = api.get_account()
    stock_metrics = [['' for m in range(1)] for i in range(len(stock_tickers_involved) * 3)]
    spdr_string = str(spyreturn) + str('%')
    spdr_list = ["Daily return of $SPY", spdr_string]

    stock_index = 0
    for stock in stock_tickers_involved:
        # the average max holdings of each stock is limited at 10% of the portfolio
        trade_size_relative_to_portfolio = 0.1
        beta = trade_size_relative_to_portfolio * float(quote_data[stock]['beta'])
        buying_power = float(account.buying_power) / 4
        stock_profit_pct = round((profit_per_symbol[stock] / buying_power) * 100, 4)
        market_returns_pct = quote_data[stock]['returns']
        # divide the 1 month risk free rate by 30 to approximate the rate of bond return for 1 day
        alpha = round((stock_profit_pct - (riskfreerate / 30)) - (beta * (spyreturn - (riskfreerate / 30))), 4)

        list1 = ["Performance of {}:".format(stock), str(market_returns_pct) + str('%')]
        list2 = ["Performance of {} relative to $SPY:".format(stock), str(round(market_returns_pct - spyreturn, 2)) + str('%')]
        list3 = ["\"Alpha\" trading performance of {}:".format(stock), str(alpha) + str('%')]

        stock_metrics[stock_index] = list1
        stock_metrics[stock_index + 1] = list2
        stock_metrics[stock_index + 2] = list3

        print(list1)
        print(list2)
        print(list3)
        stock_index += 3

    # if the total gross profit of the stock is not positive then the gross loss must be flipped in order to generate a
    # non negative percentage for the profit factor of the portfolio
    if total_gross_profit > -total_gross_loss:
        total_profit_factor = round((total_gross_profit / -total_gross_loss), 2)
    else:
        total_profit_factor = round((total_gross_profit / total_gross_loss), 2)

    if long_gross_profit > -long_gross_loss:
        long_profit_factor = round((long_gross_profit / -long_gross_loss), 2)
    else:
        long_profit_factor = round((long_gross_profit / long_gross_loss), 2)

    if short_gross_profit > -short_gross_loss:
        short_profit_factor = round((short_gross_profit / -short_gross_loss), 2)
    else:
        short_profit_factor = round((short_gross_profit / short_gross_loss), 2)

    total_percent_profitable = round(((long_winning_trades + short_winning_trades) / (total_long_trades +
                                                                                      total_short_trades)) * 100, 2)
    long_percent_profitable = round((long_winning_trades / total_long_trades) * 100, 2)
    short_percent_profitable = round((short_winning_trades / total_short_trades) * 100, 2)

    no_of_stock_metrics = len(stock_metrics)

    # this is the 2d list used to convert into a pandas dataframe for easy transcription onto an excel document
    data = [['Profit Metrics', '', '', ''],
        ['Total Net Profit:', todayspandl, net_long_profit, net_short_profit],
        ['Gross Profit:', total_gross_profit, long_gross_profit, short_gross_profit],
        ['Gross Loss:', total_gross_loss, long_gross_loss, short_gross_loss],
        ['Profit Factor:', total_profit_factor, long_profit_factor, short_profit_factor],
        ['', '', '', ''],
        ['Trade Metrics', '', '', ''],
        ['Total Number of Trades:', int(total_long_trades + total_short_trades), total_long_trades, total_short_trades],
        ['Percent Profitable:', str(total_percent_profitable) + str("%"), str(long_percent_profitable) + str('%'),
         str(short_percent_profitable) + str('%')],
        ['Average Time Held (Minutes):', avg_total_trade_hold_time.lstrip("0"), avg_long_trade_length.lstrip("0"),
         avg_short_trade_length.lstrip("0")],
        ['Winning Trades:', long_winning_trades + short_winning_trades, long_winning_trades, short_winning_trades],
        ['Average Winning Trade:', avg_winning_trade, avg_long_winning_trade, avg_short_winning_trade],
        ['Losing Trades:', long_losing_trades + short_losing_trades, long_losing_trades, short_losing_trades],
        ['Average Losing Trade:', avg_losing_trade, avg_long_losing_trade, avg_short_losing_trade],
        ['Even Trades', long_even_trades + short_even_trades, long_even_trades, short_even_trades],
        ['', '', '', ''],
        ['Stock Metrics', '', '', ''],
        spdr_list] + stock_metrics

    # if i want to add further rows in the future, simply do
    # data + 2d list

    portfolio_metrics = DataFrame(data, columns=['Performance Summary', 'All Trades', 'Long Trades', 'Short Trades'])
    sheet_name = str('Performance on ') + str(date)
    data_to_excel(portfolio_metrics)
    formatting_excel(sheet_name)
