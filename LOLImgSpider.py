import requests as r
import os
from fake_useragent import UserAgent
import time
import json
import threading

lock = threading.Lock()
# 读取配置信息
if os.path.exists(f"{os.getcwd()}/lol.json") == 0:
    print("找不到lol.json配置文件，生成配置文件中")
    file = open(f"{os.getcwd()}/lol.json", "x")
    file.write(str(json.dumps({"downloadPath": "",
                               "thread": "8"})))
    file.flush()
    file.close()
    print("生成完成！downloadPath是保存地址,请配置")
    time.sleep(10)
    exit()


# 如果配置信息是None
fJson = open(f"{os.getcwd()}/lol.json", 'r')
objJson = json.loads(fJson.read(100))
if len(str(objJson['downloadPath'])) == 0:
    print("未配置保存地址！！！，请配置。")
    time.sleep(10)
    exit()
print(f"下载路径为：{objJson['downloadPath']}")
print(f"下载线程数量为：{objJson['thread']}")


class LOLTest(threading.Thread):

    def __init__(self):
        """
        初始化
        """
        super().__init__()
        self.heroInfo = {}
        self.headers = {
            "user-agent": str(UserAgent())
        }

    def run(self):
        self.downloadThread()

    def test(self):
        """
        英雄联盟的英雄图片爬虫下载
        :return: None
        """
        # 英雄列表URL
        heroListURL = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
        # 英雄信息URL
        heroInfoURL = "https://game.gtimg.cn/images/lol/act/img/js/hero/"
        heroListJson = r.get(heroListURL,
                             headers=self.headers).text
        objectJson = json.loads(heroListJson)
        for hero in objectJson["hero"]:
            print("当前英雄ID：", hero["heroId"], "，当前英雄称号：", hero["name"], "-", hero["title"])
            heroInfo = json.loads(
                r.get(f"{heroInfoURL}{hero['heroId']}.js",
                      headers=self.headers).text)
            # 创建文件夹
            if os.path.exists(f"{objJson['downloadPath']}/{heroInfo['hero']['name']}-{heroInfo['hero']['title']}") == 0:
                os.mkdir(f"{objJson['downloadPath']}/{heroInfo['hero']['name']}-{heroInfo['hero']['title']}")
            # 以下是线程区域，限制线程
            while True:
                if len(threading.enumerate()) <= (int(objJson['thread']) + 1):
                    break
            # 线程同步 加锁
            lock.acquire()
            var = LOLTest()
            var.heroInfo = heroInfo
            var.start()
            # print(f"当前线程：{len(threading.enumerate())}")
            # 线程同步 解锁
            print(hero['name'], "-", hero['title'], "下载完成中...")
            lock.release()
        print("图片已全部下载完成!")

    def downloadThread(self):
        """
        下载线程
        :return: None
        """
        # 获取到图片列表，遍历图片
        for skins in self.heroInfo["skins"]:
            if skins["mainImg"] != "":
                # 查看是否已经下载过
                if os.path.exists(
                        f"{objJson['downloadPath']}/{skins['heroName']}-{skins['heroTitle']}/{skins['name']}.jpg") == 1:
                    continue
                # 处理异常
                try:
                    # 睡眠
                    time.sleep(2)
                    # 图片数据
                    imgContent = r.get(skins["mainImg"], headers=self.headers).content
                    # 图片名称
                    imgName = skins["name"]
                    # print(f"下载图片中：{imgName}  ...")
                    f = open(f"{objJson['downloadPath']}/{skins['heroName']}-{skins['heroTitle']}/{imgName}.jpg", "wb+")
                    f.write(imgContent)
                    f.flush()
                    f.close()
                except Exception as e:
                    print(e.args)
                    pass
                    # print("图片链接获取成功，但是下载出现异常,异常原因：", e.args)
            else:
                pass
                # print(f"图片：{skins['name']}获取链接是：null，已跳过...")
        # print(self.heroInfo["hero"]['name'], "-", self.heroInfo["hero"]['title'], "下载完成完成。")


if __name__ == '__main__':
    """
    启动程序
    """
    LOLTest().test()
