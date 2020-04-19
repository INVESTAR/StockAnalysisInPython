from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
import matplotlib.pyplot as plt

df = pdr.get_data_yahoo('005930.KS', '2017-01-01')  # ①

plt.figure(figsize=(9, 6))
plt.subplot(2, 1, 1)  # ② 
plt.title('Samsung Electronics (Yahoo Finance)')
plt.plot(df.index, df['Close'], 'c', label='Close')  # ③
plt.plot(df.index, df['Adj Close'], 'b--', label='Adj Close')  # ④
plt.legend(loc='best')
plt.subplot(2, 1, 2)  # ⑤
plt.bar(df.index, df['Volume'], color='g', label='Volume')  # ⑥
plt.legend(loc='best')
plt.show()
