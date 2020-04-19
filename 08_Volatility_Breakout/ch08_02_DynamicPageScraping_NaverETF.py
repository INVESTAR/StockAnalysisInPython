from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

# 옵션값 설정
opt = webdriver.ChromeOptions()
opt.add_argument('headless')

# 웹드라이버를 통해 네이버 금융 ETF 페이지에 접속
drv = webdriver.Chrome('C:\myPackage\chromedriver.exe', options=opt)
drv.implicitly_wait(3)
drv.get('https://finance.naver.com/sise/etf.nhn')

# 뷰티풀 수프로 테이블을 스크래핑
bs = BeautifulSoup(drv.page_source, 'lxml')
drv.quit()
table = bs.find_all("table", class_="type_1 type_etf")
df = pd.read_html(str(table), header=0)[0]

# 불필요한 열과 행을 삭제하고 인덱스를 재설정해서 출력
df = df.drop(columns=['Unnamed: 9'])
df = df.dropna()
df.index = range(1, len(df)+1)
print(df)

# 링크 주소에 포함된 종목코드를 추출하여 전체 종목코드와 종목명 출력
etf_td = bs.find_all("td", class_="ctg")
etfs = {}
for td in etf_td:
    s = str(td.a["href"]).split('=')
    code = s[-1]
    etfs[td.a.text] = code
print("etfs :", etfs)