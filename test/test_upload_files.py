import requests
import json

url = "http://127.0.0.1:11106/stastic/upload_stastic_info"

file_path = r"F:/usr/data/stastic/stastic_tags/2024-09-09.json"

response = requests.post(url, files={'file': (file_path, open(file_path, 'rb'))}, \
                         data={"save_type": "label", "save_name": "2024-09-06.json", "over_write": True})


print(response.text)

print("ok")