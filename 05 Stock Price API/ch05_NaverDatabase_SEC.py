import matplotlib.pyplot as plt
from Investar import Analyzer  # ①

mk = Analyzer.MarketDB()  # ②
df = mk.get_daily_price('005930', '2017-07-10', '2018-06-30')  # ③

plt.figure(figsize=(9, 6))
plt.subplot(2, 1, 1)
plt.title('Samsung Electronics (Investar Data)')
plt.plot(df.index, df['close'], 'c', label='Close')  # ④
plt.legend(loc='best')
plt.subplot(2, 1, 2)
plt.bar(df.index, df['volume'], color='g', label='Volume')
plt.legend(loc='best')
plt.show()