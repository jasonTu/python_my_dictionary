import sys
import uuid
import requests
import hashlib
import time
from imp import reload

import time

# reload(sys)


LANG_TYPE_ENG = 0
LANG_TYPE_ZH = 1


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def detect(q):
    if 'a' <= q <= 'z' or 'A' <= q<= 'Z':
        return LANG_TYPE_ENG
    else:
        return LANG_TYPE_ZH


class MyDictionary:
    def __init__(self):
        self.YOUDAO_URL = 'https://openapi.youdao.com/api'
        self.APP_KEY = ''
        self.APP_SECRET = ''

    def do_request(self, data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(self.YOUDAO_URL, data=data, headers=headers)

    def record_search(self, word):
        """Record serach only."""
        with open('word_list.txt', 'a+') as fp:
            fp.write(word+'\n')

    def meaning(self, word):
        lang_type = detect(word[0])
        data = {}
        data['from'] = 'auto'
        if lang_type == LANG_TYPE_ENG:
            data['to'] = 'zh'
        else:
            data['to'] = 'en'
        data['signType'] = 'v3'
        curtime = str(int(time.time()))
        data['curtime'] = curtime
        salt = str(uuid.uuid1())
        signStr = self.APP_KEY + truncate(word) + salt + curtime + self.APP_SECRET
        sign = encrypt(signStr)
        data['appKey'] = self.APP_KEY
        data['q'] = word
        data['salt'] = salt
        data['sign'] = sign
        # data['vocabId'] = "您的用户词表ID"

        response = self.do_request(data)
        result = {}
        contentType = response.headers['Content-Type']
        if contentType == "audio/mp3":
            millis = int(round(time.time() * 1000))
            filePath = "合成的音频存储路径" + str(millis) + ".mp3"
            fo = open(filePath, 'wb')
            fo.write(response.content)
            fo.close()
        else:
            resp = response.json()
            # print(resp)
            trans = resp['translation']
            # print(trans)
            # print(response.content)
        result['translate'] = resp['translation']
        if 'web' in resp and resp['web']:
            for web_item in resp['web']:
                key = web_item['key']
                value = web_item['value']
                result[key] = value
        return result


if __name__ == '__main__':
    q = "工作"
    my_dict = MyDictionary()
    print(my_dict.meaning(q))
