import matplotlib.pyplot as plt
from Investar import Analyzer

mk = Analyzer.MarketDB()
df = mk.get_daily_price('NAVER', '2019-01-02')
  
df['MA20'] = df['close'].rolling(window=20).mean()  # ①
df['stddev'] = df['close'].rolling(window=20).std() # ②
df['upper'] = df['MA20'] + (df['stddev'] * 2)   # ③
df['lower'] = df['MA20'] - (df['stddev'] * 2)   # ④
df = df[19:]  # ⑤

plt.figure(figsize=(9, 5))
plt.plot(df.index, df['close'], color='#0000ff', label='Close')    # ⑥
plt.plot(df.index, df['upper'], 'r--', label = 'Upper band')       # ⑦
plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
plt.plot(df.index, df['lower'], 'c--', label = 'Lower band')
plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')  # ⑧ 
plt.legend(loc='best')
plt.title('NAVER Bollinger Band (20 day, 2 std)')
plt.show()
