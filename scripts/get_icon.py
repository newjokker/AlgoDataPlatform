



from PIL import Image

# 打开现有的图片文件
img = Image.open(r'F:\Code\algodataplatform\app\static\icon.png')

# 转换并保存为.ico格式
img.save(r'F:\Code\algodataplatform\app\static\favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
