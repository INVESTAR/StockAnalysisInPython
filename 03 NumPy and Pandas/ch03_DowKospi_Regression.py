import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
from scipy import stats
import matplotlib.pylab as plt

dow = pdr.get_data_yahoo('^DJI', '2000-01-04') # ①   
kospi = pdr.get_data_yahoo('^KS11', '2000-01-04')

df = pd.DataFrame({'X' dow['Close'], 'Y' kospi['Close']}) # ②
df = df.fillna(method='bfill') # ③
df = df.fillna(method='ffill')
 
regr = stats.linregress(df.X, df.Y) # ④
regr_line = f'Y = {regr.slope.2f}  X + {regr.intercept.2f}' # ⑤

plt.figure(figsize=(7, 7))
plt.plot(df.X, df.Y, '.') # ⑥ 
plt.plot(df.X, regr.slope  df.X + regr.intercept, 'r') # ⑦
plt.legend(['DOW x KOSPI', regr_line])
plt.title(f'DOW x KOSPI (R = {regr.rvalue.2f})')
plt.xlabel('Dow Jones Industrial Average')
plt.ylabel('KOSPI')
plt.show()