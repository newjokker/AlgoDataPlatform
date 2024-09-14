



from PIL import Image

# 打开现有的图片文件
img = Image.open(r'/home/ldq/Code/AlgoDataPlatform/app/static/txkj.jpg')

# 转换并保存为.ico格式
img.save(r'/home/ldq/Code/AlgoDataPlatform/app/static/favicon2.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
