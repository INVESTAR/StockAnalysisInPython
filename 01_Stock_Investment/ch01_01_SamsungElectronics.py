import matplotlib.pyplot as plt
from Investar import Analyzer

mk = Analyzer.MarketDB()
df = mk.get_daily_price('삼성전자', '1998-04-27', '2018-04-27')
"""
>>> df
              code        date     open  ...  volume       MA20      MA200
date                                     ...                              
1998-04-27  005930  1998-04-27    66800  ...  187010        NaN        NaN
1998-04-28  005930  1998-04-28    65000  ...  174220        NaN        NaN
1998-04-29  005930  1998-04-29    66900  ...  238910        NaN        NaN
1998-04-30  005930  1998-04-30    70500  ...  616240        NaN        NaN
1998-05-02  005930  1998-05-02    72000  ...  236600        NaN        NaN
...            ...         ...      ...  ...     ...        ...        ...
2018-04-23  005930  2018-04-23  2550000  ...  232380  2478450.0  2513175.0
2018-04-24  005930  2018-04-24  2592000  ...  315406  2479650.0  2513805.0
2018-04-25  005930  2018-04-25  2461000  ...  332292  2483900.0  2514520.0
2018-04-26  005930  2018-04-26  2521000  ...  360931  2491650.0  2515750.0
2018-04-27  005930  2018-04-27  2669000  ...  606216  2501100.0  2517250.0

[4967 rows x 10 columns]
"""
df['MA20'] = df['close'].rolling(window=20).mean()   
df['MA200'] = df['close'].rolling(window=200).mean() 

plt.figure(figsize=(9, 7))
plt.plot(df.index, df['close'], color='cyan', label='Close')
plt.plot(df.index, df['MA20'], 'm--', label='MA20')
plt.plot(df.index, df['MA200'], 'r--', label='MA200')
plt.legend(loc='best')
plt.title('Samsung Electronics')
plt.grid(color='gray', linestyle='--')
plt.yticks([65300, 500000, 1000000, 1500000, 2000000, 2500000, 2650000])
plt.xticks(['1998-04-27', '2002-04-27', '2006-04-27', '2010-04-27', '2014-04-27', '2018-04-27'])
plt.show()
