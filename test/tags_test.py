import unittest 
from config import SERVER_HOST, SERVER_PORT
import requests
import uuid
import json


LOCAL_SERVER_HOST = "192.168.3.50"
# LOCAL_SERVER_HOST = "127.0.0.1"

class Test_TestIncrementDecrement(unittest.TestCase):
    
    # def test_get_tags(self):
    #     url = f"http://{LOCAL_SERVER_HOST}:{SERVER_PORT}/tag/get_tags"
    #     response = requests.get(url)
    #     self.assertEqual(response.status_code, 200)

    # def test_add_tag(self):
    #     url = f"http://{LOCAL_SERVER_HOST}:{SERVER_PORT}/tag/add_tag"
    #     data = {"tag_name": f"test_jokker{str(uuid.uuid1())}", "tag_describe": "test tag name : test"}
    #     response = requests.post(url, json=data)
    #     self.assertEqual(response.status_code, 200)

    def test_get_add_delete_tag(self):
        # add
        url = f"http://{LOCAL_SERVER_HOST}:{SERVER_PORT}/tag/add_tag"
        random_tag_name = f"test_jokker{str(uuid.uuid1())}"
        data = {"tag_name": random_tag_name, "tag_describe": "test tag name : test"}
        response = requests.post(url, json=data)     
        print(f"* add tag : {random_tag_name}")
        print(url)
        self.assertEqual(response.status_code, 200)
        # get 
        url_get_tag_info    = f"http://{LOCAL_SERVER_HOST}:{SERVER_PORT}/tag/get_tags"
        response = requests.get(url_get_tag_info)
        tag_info = json.loads(response.text)
        print(f"* get tag info : {tag_info}")
        self.assertEqual(response.status_code, 200)
        # delete
        url_delete_tag      = f"http://{LOCAL_SERVER_HOST}:{SERVER_PORT}/tag/delete_tag"
        remove_tags = [x for x in tag_info.keys() if str(x).startswith("test_jokker")]
        for each_tag in remove_tags:
            data = {"tag_name": each_tag}
            response = requests.post(url_delete_tag, json=data)
            print(f"* delete tag : {each_tag}")
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    
    unittest.main()
