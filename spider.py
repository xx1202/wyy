import requests
import json

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base64 import b64encode
import logging


def encrypt_aes(text, key, iv):
    """
    使用AES-CBC加密文本
    :param text: 待加密的文本
    :param key: 加密密钥
    :param iv: 初始向量
    :return: 加密后的文本（Base64编码）
    """
    try:
        # 创建AES加密对象
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        # 对文本进行填充
        padded_text = pad(text.encode('utf-8'), AES.block_size)
        # 加密并编码
        ciphertext = cipher.encrypt(padded_text)
        return b64encode(ciphertext).decode('utf-8')
    except Exception as e:
        logging.error(f"Encryption error: {e}")
        return None


class Spider:
    def __init__(self):
        # 初始化HTTP头部信息和加密密钥
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': 'https://music.163.com/weapi/comment/resource/comments/get?csrf_token=d5b7e365dd0cdf7315a9688eb41096f7'
        }
        self.encSecKey = "ac120b775a368f6cdf196f173ac16bccaa08e8589fdd824f7445cb71a6f12f7a25da019240ce2f69a214ef34ba2795b057b1cf4fd24fbf4bd9f78167c9c69de4ee8be3bb8bb9119e2a0328219497864558363bc8e5c8a7999822f127dc0d7fc3bbf0a53f3e2e091eba811eb57558dd6290ab4224f636cea2d264bb2ed7c7cee8"
        self.iv = "0102030405060708"
        self.g = "0CoJUm6Qyw8W8jud"
        self.i = "4BfsFyBWTSe0C5eQ"
        logging.basicConfig(level=logging.INFO)

    def b(self, a, b):
        """
        调用AES加密函数
        :param a: 待加密的文本
        :param b: 加密密钥
        :return: 加密后的文本
        """
        return encrypt_aes(a, b, self.iv)

    # 获取加密的请求参数
    def get_encText(self, offset):
        # 构造请求数据
        d = {
            'csrf_token': '',
            "offset": offset,
            "total": "true" if offset == 0 else "false",
            "limit": "20",
            'rid': '',
        }
        d_json = json.dumps(d)
        # 调用两次加密函数
        encText = self.b(d_json, self.g)
        if encText:
            encText = self.b(encText, self.i)
        return encText

    # 发送POST请求获取评论数据
    def post(self, url, encText, encSecKey):
        try:
            data = {
                'params': encText,
                'encSecKey': encSecKey
            }
            # 发送POST请求
            resp = requests.post(url, headers=self.headers, data=data)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            return None

    # 解析评论数据
    def parse_comment(self, resp):
        comments = []
        try:
            users = resp['comments']
            for user in users:
                content = user['content']
                created_at = user['timeStr']
                username = user['user']['nickname']
                likes = user['likedCount']
                comments.append((username, content, created_at, likes))
        except KeyError as e:
            logging.error(f"Parsing error: {e}")
        return comments

    # 获取指定音乐ID的评论
    def get_comments(self, music_id, page):
        url = f'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{music_id}/?csrf_token='
        limit = 20
        offset = 0
        comms = []
        while offset // 20 < page:
            encText = self.get_encText(offset)
            if not encText:
                break
            resp = self.post(url, encText, self.encSecKey)
            if not resp:
                break
            data = self.parse_comment(resp)
            if data:
                print(data)
                comms += data
            offset += limit
        return comms

