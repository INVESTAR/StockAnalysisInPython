from slacker import Slacker
from datetime import datetime

slack = Slacker('xoxb-341411373331-390645946323-wPFYKNbhlgef4bMUiP1CvSyI')
def dbgout(message):
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    slack.chat.post_message('#etf-algo-trading', strbuf)

#dbgout("This is test log.")

#-----------------------------------------------------------------------------------

import ctypes
import win32com.client
# CREON Plus 공통 Object
cpStatus = win32com.client.Dispatch('CpUtil.CpCybos')      # 시스템 상태 정보 
cpTradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil') # 주문 관련 도구 함수 
cpCodeMgr = win32com.client.Dispatch('CpUtil.CpStockCode') # 종목코드
cpStock = win32com.client.Dispatch('DsCbo1.StockMst')      # 주식 종목별 정보
cpOhlc = win32com.client.Dispatch('CpSysDib.StockChart')   # 시가 고가 저가 종가 정보
cpBalance = win32com.client.Dispatch('CpTrade.CpTd6033')   # 계좌 정보
cpCash = win32com.client.Dispatch('CpTrade.CpTdNew5331A')  # 주문 가능 금액 
cpOrder = win32com.client.Dispatch('CpTrade.CpTd0311')     # 주문

# CREON Plus 시스템 점검 함수크
def check_creon_system():
    # 관리자 권한으로 프로세스 실행 여부
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print('check_creon_system() : admin user -> FAILED')
        return False
 
    # 연결 여부 체크
    if (cpStatus.IsConnect == 0):
        print('check_creon_system() : connect to server -> FAILED')
        return False
 
    # 주문 관련 초기화 
    if (cpTradeUtil.TradeInit(0) != 0):
        print('check_creon_system() : init trade -> FAILED')
        return False
    
    return True

#print('check_creon_system() ->', check_creon_system())

#-------------------------------------------------------------------------------------------

import pandas as pd
import calendar
import time
import getpass
import codecs
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import os
import sys

def get_current_price(code):
    cpStock.SetInputValue(0, code)
    cpStock.BlockRequest()
    item = {}
    item['cur_price'] = cpStock.GetHeaderValue(11)  # 현재가
    #item['volatility'] = cpStock.GetHeaderValue(12) # 전일대비
    item['ask'] =  cpStock.GetHeaderValue(16)       # 매수호가
    item['bid'] =  cpStock.GetHeaderValue(17)       # 매도호가  
    #item['PER'] =  cpStock.GetHeaderValue(28)       # PER
    #print('get_current_price({}) returned {}'.format(code, item['cur_price']), item)
    return item['cur_price'], item['ask'], item['bid']

#get_current_price('A305080')

def get_ohlc(code, qty):
    cpOhlc.SetInputValue(0, code)      # 종목코드
    cpOhlc.SetInputValue(1, ord('2'))  # 1:기간, 2:개수
    cpOhlc.SetInputValue(4, qty)       # 요청개수
    cpOhlc.SetInputValue(5, [0, 2, 3, 4, 5]) # 0:날짜, 2~5:OHLC
    cpOhlc.SetInputValue(6, ord('D'))  # 일단위
    cpOhlc.SetInputValue(9, ord('1'))  # 0:무수정주가, 1:수정주가
    cpOhlc.BlockRequest()
    count = cpOhlc.GetHeaderValue(3)   # 3:수신개수
    columns = ['open', 'high', 'low', 'close']
    index = []
    rows = []
    for i in range(count):
        index.append(cpOhlc.GetDataValue(0, i))
        rows.append([cpOhlc.GetDataValue(1, i), cpOhlc.GetDataValue(2, i), cpOhlc.GetDataValue(3, i), cpOhlc.GetDataValue(4, i)])
    df = pd.DataFrame(rows, columns=columns, index=index)
    return df

#print(get_ohlc('A305080', 10))


cpTradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil') # 주문 관련 도구 함수 
cpBalance = win32com.client.Dispatch("CpTrade.CpTd6033")   # 계좌 정보

def get_stock_balance(code):
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]      # 계좌번호
    accFlag = cpTradeUtil.GoodsList(acc, 1) # 주식상품 구분 (-1:전체, 1:주식, 2:선물/옵션)
    cpBalance.SetInputValue(0, acc)         # 계좌번호
    cpBalance.SetInputValue(1, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
    cpBalance.SetInputValue(2, 50)          # 요청 건수(최대 50)
    cpBalance.BlockRequest()
     
    if code == 'ALL':
        dbgout('계좌명: ' + str(cpBalance.GetHeaderValue(0)))
        dbgout('결제잔고수량 : ' + str(cpBalance.GetHeaderValue(1)))
        dbgout('평가금액: ' + str(cpBalance.GetHeaderValue(3)))
        dbgout('평가손익: ' + str(cpBalance.GetHeaderValue(4)))
        dbgout('종목수: ' + str(cpBalance.GetHeaderValue(7)))
    
    stocks = []
    for i in range(cpBalance.GetHeaderValue(7)):
        stock_code = cpBalance.GetDataValue(12, i)  # 종목코드
        stock_name = cpBalance.GetDataValue(0, i)   # 종목명
        stock_qty = cpBalance.GetDataValue(15, i)   # 수량
        if code == 'ALL':
            dbgout(str(i+1) + ' ' + stock_code + '(' + stock_name + ')' + ':' + str(stock_qty))
            stocks.append({'code': stock_code, 'name': stock_name, 'qty': stock_qty})
        if stock_code == code:  
            return stock_name, stock_qty
    if code == 'ALL':
        return stocks
    else:
        stock_name = cpCodeMgr.CodeToName(code)
        return stock_name, 0

#print('get_stock_balance("A305080") returned', get_stock_balance('A305080'))


def get_current_cash():
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]  # 계좌번호
    #print('get_current_cash() -> acc :', acc)
    accFlag = cpTradeUtil.GoodsList(acc, 1)  # 주식상품 구분 (-1:전체, 1:주식, 2:선물/옵션)
    cpCash.SetInputValue(0, acc)             # 계좌번호
    cpCash.SetInputValue(1, accFlag[0])      # 상품구분 - 주식 상품 중 첫번째
    cpCash.BlockRequest()
    
    #print('증거금100%주문가능금액 :', cpCash.GetHeaderValue(9))
    #print('현금주문가능금액 :', cpCash.GetHeaderValue(10))
    print('예수금 :', cpCash.GetHeaderValue(45))
    return cpCash.GetHeaderValue(9)

def get_target_price(code):
    try:
        time_now = datetime.now()
        str_today = time_now.strftime('%Y%m%d')
        ohlc = get_ohlc(code, 10)
        if str_today == str(ohlc.iloc[0].name):
            lastday = ohlc.iloc[1]
        else:
            lastday = ohlc.iloc[0]                                      
        today_open = lastday[3]
        lastday_high = lastday[1]
        lastday_low = lastday[2]
        target_price = today_open + (lastday_high - lastday_low) * 0.5
        return target_price
    except Exception as ex:
        dbgout("`get_target_price() -> exception! " + str(ex) + "`")
        return None

#print('get_target_price(A305080) :', get_target_price('A305080'))


def get_movingaverage(code, window):
    try:
        time_now = datetime.now()
        str_today = time_now.strftime('%Y%m%d')
        ohlc = get_ohlc(code, 20)
        if str_today == str(ohlc.iloc[0].name):
            lastday = ohlc.iloc[1].name
        else:
            lastday = ohlc.iloc[0].name
        closes = ohlc['close'].sort_index()         
        ma = closes.rolling(window=window).mean()
        return ma.loc[lastday]
    except Exception as ex:
        dbgout('get_movingaverage(' + str(window) + ') -> exception! ' + str(ex))
        return None

#get_movingaverage('A305080', 5)

		
def buy_etf(code):
    try:
        global bought_list
        if code in bought_list: # 보유 종목이면 안 사도록
            return False
        buy_qty = 0
                
        time_now = datetime.now()
        current_price, ask_price, bid_price = get_current_price(code)
        target_price = get_target_price(code)
        ma5_price = get_movingaverage(code, 5)
        ma10_price = get_movingaverage(code, 10)
        if ask_price > 0:
            buy_qty = current_cash // ask_price
        stock_name, stock_qty = get_stock_balance(code)

        if time_now.minute == 0 and time_now.second == 30:
            get_stock_balance('ALL')
    
        if current_price > target_price and current_price > ma5_price and current_price > ma10_price:
            print('`' + str(stock_name) + '(' + str(code) + ') ' + str(buy_qty) + 'EA : current_price(' + str(current_price) + ') meets the buy condition!`')
            if len(bought_list) > target_buy_count:
                print('len(bought_list): ', len(bought_list))
                return
            
            cpTradeUtil.TradeInit()
            acc = cpTradeUtil.AccountNumber[0]  # 계좌번호
            accFlag = cpTradeUtil.GoodsList(acc, 1)  # 주식상품 구분 (-1:전체, 1:주식, 2:선물/옵션)
                
            #print("<최유리 FOK 매수 주문>")
            cpOrder.SetInputValue(0, "2")  # 2: 매수
            cpOrder.SetInputValue(1, acc)  # 계좌번호
            cpOrder.SetInputValue(2, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
            cpOrder.SetInputValue(3, code)  # 종목코드
            cpOrder.SetInputValue(4, buy_qty)  # 매수수량
            cpOrder.SetInputValue(7, "2")  # 주문 조건 구분 코드, 0: 기본 1: IOC(Immediate or Cancel) 2:FOK(Fill or Kill)  
            cpOrder.SetInputValue(8, "12")  # 주문호가 구분코드 - 01:보통, 03:시장가, 05 조건부지정가, 12:최유리지정가, 13 최우선 지정가

            # 매수 주문 요청
            ret = cpOrder.BlockRequest()
            print('최유리 FOK 매수 cpOrder.BlockRequest() ->', stock_name, code, buy_qty, 'EA -> returned', ret)
            if ret == 4:
                remainTime = cpStatus.LimitRequestRemainTime
                print('주의: 주문 연속 통신 제한에 걸림. 대기 시간 :', remainTime/1000)
                time.sleep(remainTime/1000)
                return False
            
            time.sleep(2)
            print('현금주문가능금액 :', current_cash)
            stock_name, bought_qty = get_stock_balance(code)
            print('get_stock_balance :', stock_name, stock_qty)
            if bought_qty > 0:
                bought_list.append(code)
                dbgout("`buy_etf("+ str(stock_name) + ' : ' + str(code) + ") -> " + str(bought_qty) + "EA bought!" + "`")
    except Exception as ex:
        dbgout("`buy_etf("+ str(code) + ") -> exception! " + str(ex) + "`")

#buy_etf('A305080')

def sell_etf(code):
    try:
        dbgout('`sell_etf(' + str(code) + ') -> START`')
        current_price, ask_price, bid_price = get_current_price(code)
        print('current_price :', current_price)
        print('ask_price :', ask_price)
        print('bid_price :', bid_price)
        
        stock_name, sell_qty = get_stock_balance(code)
        print('get_stock_balance :', stock_name, sell_qty)
        if sell_qty == 0:
            return False
        
        cpTradeUtil.TradeInit()
        acc = cpTradeUtil.AccountNumber[0]  # 계좌번호
        accFlag = cpTradeUtil.GoodsList(acc, 1)  # 주식상품 구분 (-1:전체, 1:주식, 2:선물/옵션)
    
        print('<매도 주문> :', code, bid_price, sell_qty)
        cpOrder.SetInputValue(0, "1")  # CpTrade.CpTd0311, 1:매도, 2: 매수
        cpOrder.SetInputValue(1, acc)  # 계좌번호
        cpOrder.SetInputValue(2, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
        cpOrder.SetInputValue(3, code)  # 종목코드
        cpOrder.SetInputValue(4, sell_qty)  # 매도수량
        cpOrder.SetInputValue(5, bid_price)  # 주문단가
        cpOrder.SetInputValue(7, "0")  # 주문 조건 구분 코드, 0: 기본 1: IOC(Immediate or Cancel) 2:FOK(Fill or Kill)  
        cpOrder.SetInputValue(8, "01")  # 주문호가 구분코드 - 01:보통, 03:시장가, 05 조건부지정가, 12:최유리지정가, 13 최우선 지정가
 
        # 매도 주문 요청
        ret = cpOrder.BlockRequest()
        print('매도 cpOrder.BlockRequest() -> returned', ret)
        if ret == 4:
            remainTime = cpStatus.LimitRequestRemainTime
            print('주의: 주문 연속 통신 제한에 걸렸음. 대기 필요 시간', remainTime/1000)
            time.sleep(remainTime/1000)
            return False
        time.sleep(1)
        #bal = exch.fetch_balance()
        print('current_cash :', current_cash)
        
        stock_name, sell_qty = get_stock_balance(code)
        print('get_stock_balance :', stock_name, sell_qty)
        
        dbgout('`sell_etf(' + str(code) + ') -> END`')
    except Exception as ex:
        dbgout("sell_etf("+ str(code) + ") -> exception! " + str(ex))

def sell_all():
    try:
        dbgout('`sell_all() -> START`')   
                
        cpTradeUtil.TradeInit()
        acc = cpTradeUtil.AccountNumber[0]  # 계좌번호
        accFlag = cpTradeUtil.GoodsList(acc, 1)  # 주식상품 구분 (-1:전체, 1:주식, 2:선물/옵션)
        
        while True:    
            stocks = get_stock_balance('ALL')

            total_qty = 0 
            for s in stocks:
                total_qty += s['qty']
            if total_qty == 0:
                return True
            
            for s in stocks:
                if s['qty'] != 0:                   
                    cpOrder.SetInputValue(0, "1")  # CpTrade.CpTd0311, 1:매도, 2: 매수
                    cpOrder.SetInputValue(1, acc)  # 계좌번호
                    cpOrder.SetInputValue(2, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
                    cpOrder.SetInputValue(3, s['code'])  # 종목코드
                    cpOrder.SetInputValue(4, s['qty'])  # 매도수량
                    #cpOrder.SetInputValue(5, "0")  # 주문단가
                    cpOrder.SetInputValue(7, "1")  # 주문 조건 구분 코드, 0: 기본 1: IOC(Immediate or Cancel) 2:FOK(Fill or Kill)  
                    cpOrder.SetInputValue(8, "12")  # 주문호가 구분코드 - 01:보통, 03:시장가, 05 조건부지정가, 12:최유리지정가, 13 최우선 지정가
 
                    # 최유리 IOC 매도 주문 요청
                    ret = cpOrder.BlockRequest()
                    print('최유리 IOC 매도', s['code'], s['name'], s['qty'], '-> cpOrder.BlockRequest() -> returned', ret)
                    if ret == 4:
                        remainTime = cpStatus.LimitRequestRemainTime
                        print('주의: 주문 연속 통신 제한에 걸렸음. 대기해서 주문할 지 여부 판단이 필요 남은 시간', remainTime)
                        time.sleep(remainTime/1000)
            time.sleep(2)
        get_stock_balance('ALL')                    
        dbgout('`sell_etf("ALL") -> END`')
    except Exception as ex:
        dbgout("sell_etf('ALL') -> exception! " + str(ex))



try:
    #my_symbol = 'A233740'
    # 8/29(목) 장전 평가금액 : 23312553
    # 8/30(금) 장전 평가금액 : 23453393
    # 9/2(월) 장전 100%증거금주문가능금액 : 22965553
    # 9/3(화) 장전 평가금액 : 23277050
    #symbol_list = ['A305080', 'A319640', 'A225130', 'A233740', 'A267770', 'A204480', 'A122630', 'A292570', 'A261250','A251340','A150460', 'A132030', 'A144600', 'A204480', 'A245710']
    symbol_list = ['A144600', 'A132030', 'A251340', 'A133690', 'A204480', 'A169950', 'A192090', 'A283580', 'A168580', 'A182480', 'A305080', 'A143850']
    bought_list = []
    buy_amount = 0.24
    target_buy_count = 4 # 함수 내에서 값 변경 불가
    print('check_creon_system() :', check_creon_system())
    stocks = get_stock_balance('ALL') # 전체 계좌 표시
    total_cash = int(get_current_cash())
    current_cash = total_cash * buy_amount
    print('100%증거금주문가능금액 :', total_cash)
    print('종목별 비율 :', buy_amount)
    print('종목별 주문금액 :', current_cash)
        
    time_now = datetime.now()
    today = datetime.today().weekday()
    print('시작시간 :', time_now.strftime('%m/%d %H:%M:%S'))
    if today == 5 or today == 6:
        print('CAUTION: Today is', 'Saturday.' if today == 5 else 'Sunday.')
        sys.exit(0)

    #sell_all() # 주석 제거 시 ETF가 있을 경우 무조건 팔고 시작하니 주의할 것..... 
    
    while True:
        time_now = datetime.now()
        time_start = time_now.replace(hour=9, minute=5, second=0, microsecond=0)
        time_end = time_now.replace(hour=15, minute=15, second=0, microsecond=0)
        today = datetime.today().weekday()

        if 0 <= today <= 4:
            if time_start < time_now < time_end :
                for sym in symbol_list:
                    if len(bought_list) <= target_buy_count:
                        buy_etf(sym)
                        time.sleep(1)

        time_now = datetime.now()
        time_closing_start = time_now.replace(hour=15, minute=15, second=0, microsecond=0)
        time_closing_end = time_now.replace(hour=15, minute=30, second=0, microsecond=0)
        today = datetime.today().weekday()
        if 0 <= today <= 4:
            if time_closing_start < time_now < time_closing_end:
                sell_all()

        time_now = datetime.now()
        time_exit = time_now.replace(hour=15, minute=30, second=0, microsecond=0)
        if 0 <= today <= 4:
            if time_exit < time_now:
                dbgout('`self-destructed!`')
                sys.exit(0)

        time.sleep(1)

except Exception as ex:
    dbgout('`main() -> exception! ' + str(ex) + '`')

