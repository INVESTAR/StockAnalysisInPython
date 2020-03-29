import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt

url = 'httpsfinance.naver.comitemsise_day.nhncode=068270&page=1'
with urlopen(url) as doc
    html = BeautifulSoup(doc, 'lxml') 
    pgrr = html.find('td', class_='pgRR')
    s = str(pgrr.a['href']).split('=')
    last_page = s[-1]  

df = pd.DataFrame()
sise_url = 'httpsfinance.naver.comitemsise_day.nhncode=068270'  
for page in range(1, int(last_page)+1)
    page_url = '{}&page={}'.format(sise_url, page)  
    df = df.append(pd.read_html(page_url, header=0)[0])

df = df.dropna()
df = df.iloc[030]  # ①
df = df.sort_values(by='날짜')  # ②

plt.title('Celltrion (close)')
plt.xticks(rotation=90)  # ③
plt.plot(df['날짜'], df['종가'], 'co-')  # ④
plt.show()