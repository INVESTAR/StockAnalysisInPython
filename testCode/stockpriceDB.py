from pandas_datareader import data as pdr
import yfinance as yf

import matplotlib.pyplot as plt

yf.pdr_override()

# samsung electronics
sec = pdr.get_data_yahoo('005930.KS', start = '2018-05-04')
# microsoft
msft = pdr.get_data_yahoo("MSFT",start = '2018-05-04')
amzn = pdr.get_data_yahoo("AMZN", start = '2018-05-04')

plt.plot(sec.index, sec.Close, 'b', label ="Samsung Electronics")
plt.plot(amzn.index, amzn.Close, 'r--', label ="Amazon")
plt.plot(msft.index, msft.Close, 'g--', label = "Microsoft")

plt.legend(loc = 'best')
plt.show()

