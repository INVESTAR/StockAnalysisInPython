import requests
from PIL import Image
import hashlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# 2.8.1 리퀘스트로 인터넷에서 이미지 파일 가져오기
url = 'http://bit.ly/2JnsHnT'
r = requests.get(url, stream=True).raw

# 2.8.2 필로우로 이미지 보여주기
img = Image.open(r)
print("img : ", img.get_format_mimetype)
img.show()
img.save('src.png')

# 2.8.3 'with ~ as 파일 객체:'로 이미지 파일 복사
BUF_SIZE = 1024
with open('src.png', 'rb') as sf, open('dst.png', 'wb') as df:
    while True:
        data = sf.read(BUF_SIZE) 
        if not data:
            break
        df.write(data)

# 2.8.4 SHA-256으로 파일 복사 검증하기
sha_src = hashlib.sha256()
sha_dst = hashlib.sha256()

with open('src.png', 'rb') as sf, open('dst.png', 'rb') as df:
    sha_src.update(sf.read())  
    sha_dst.update(df.read())

print("src.png's hash : {}".format(sha_src.hexdigest()))
print("dsc.png's hash : {}".format(sha_dst.hexdigest()))

# 2.8.5 맷플롯립으로 이미지 가공하기
plt.suptitle('Image Processing', fontsize=18)
plt.subplot(1, 2, 1) # 1행 2열의 영역에서 첫 번째 영역으로 지정
plt.title('Original Image')
plt.imshow(mpimg.imread('src.png')) # 원본 파일을 읽어서 이미지로 표시

plt.subplot(122) # 1행 2열의 영역에서 두 번째 영역으로 지정 
plt.title('Pseudocolor Image')
dst_img = mpimg.imread('dst.png')
pseudo_img = dst_img [:, :, 0]  # 의사 색상 적용
plt.imshow(pseudo_img) 
plt.show()


