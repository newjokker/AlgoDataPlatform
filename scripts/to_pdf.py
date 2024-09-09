


import pdfkit

# 将网页转换为PDF
# pdfkit.from_url('http://google.com', r'F:/usr/data/test.pdf')

# 或者将字符串形式的HTML转换为PDF
config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf")
html = "<h1>Hello World!</h1>"
pdfkit.from_string(html, r'F:/usr/data/test.pdf')