# -*- coding:utf-8 -*-
'''
@Description: 网易云音乐

http://music.163.com/song/media/outer/url?id={}.mp3
http://music.163.com/api/song/lyric?id={}&lv=1&kv=1&tv=-1

http://m10.music.126.net/20190801204241/e94866c5f9be9c69eac9540814b522ea/yyaac/065f/0e0e/5408/15a213070e9dcc8e4cc1cb51aa0f65bc.m4a

@Author: lamborghini1993
@Date: 2019-08-01 16:44:10
@UpdateDate: 2019-08-03 10:29:28
'''

import copy
import json
import os
import re

import scrapy

from .. import settings
from ..items import Music163Item


class Music163Spider(scrapy.Spider):
    name = 'music163'
    m_Url = "https://music.163.com/weapi/artist/top?csrf_token="
    m_Heards = {
        "content-type": "application/x-www-form-urlencoded",
        "cookie": "_ntes_nnid=22bf677fee1e1181291e514a9ad8f58f,1544855351895; _ntes_nuid=22bf677fee1e1181291e514a9ad8f58f; __oc_uuid=eb44f5e0-a79d-11e9-9164-81f23f00fc2d; hb_MA-802E-608D19012973_source=open.163.com; _iuqxldmzr_=32; WM_TID=Yf9cw%2B9l0XZFFQBAQQZ9pQuiPnlSg8jq; playerid=83991781; WM_NI=A79qCleyW8nVMet%2Bqe637isAt9l3IvlxKxEqX0toFujHp%2FTXC4S8NJyRKyjzMnQp6DE%2Ba8%2BWBC%2FvHQRoaMpL7LIfiW7x%2B6OJXB6diFpxXNeuSQXn0af%2BFsllL17jR0YCdlE%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eea9b133b89bbc95e74fb7ac8fb6c15e968a9faeb779859996d5c64aa2b481a3f62af0fea7c3b92a83e9f792c268a7a799d9ed5e8fbbbcccf46ff6edf98af24bb8e7a4d4cc7eb0a88599c87b9cf0bc90c57faa98c0d0d75481ec9dd9cd42bb8e859ae9728fb29f91b55087f5afd9aa5d829de197cb5b92b1afaef348f5948787ec5df5a8e5d7ce429c9efa85ec4eb4a898afe87f918f988fb36ba6f58a94ef6890eff98bd13c9b9dac8dc837e2a3; JSESSIONID-WYYY=tmu6mcJx89QyxyT6Jv6JjTl7q65vvidC4rf64I%5CXPUG8ddXFH%5CMmmUIrOnUe2GvRzk%5CfVF5xQWyC89qR1zpM4fXUr2mdqrya%2BTeOT3Htbnup5J7UVHBxmqIpibEJRnJGVBhuXTS7uWNtlUZZQueD7xDNu9bRtvBPjT0fagVETTyyj2G%2F%3A1564649099793",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
        "referer": "https://music.163.com/",
    }
    m_Body = {
        "params": "T3FUfv1HFYAu5vw3+u3PYrJInvvq8fshVfBMSA7GFfxBq/dVj6n0p4/70ddpH5oXXF1ENnBmjIu8sx/gqfboObNU9N+JIH43qa1mD2/ecqcIp3zFkixPz9C0VkjVq3mj",
        "encSecKey": "0ca39101af7581b07bec6a8aadc7fe4f3a0bdce22576345d9abd6f722cf59d63b56db328d240efc912061c9dc6573aa441f6a88dea3c7523c88aa2c7cdf98f5ff549d6929e7eb0c231a0d4df1039aea9e3d8d3a8490b80c898ac4979caeff44f28c4a4624a3f071a475a321e0c79775f10c958cb3d994b10032e8d76468c5c04",
    }
    m_PrefixUrl = "https://music.163.com/"

    def start_requests(self):
        yield scrapy.FormRequest(url=self.m_Url, headers=self.m_Heards, formdata=self.m_Body)
        # yield scrapy.Request(self.m_Url, callback=self.parse2file, method="POST", headers=self.m_Heards, body=json.dumps(self.m_Body))  # 这种获取不到

    def re_fold(self, fold):
        fold_name = re.sub(r'[？?\\*|"“”<>:/()]', '', fold)
        fold_name = fold_name.strip(" .")
        return fold_name

    def parse2file(self, response):
        filename = "temp/" + response.url.split("/")[2] + ".html"
        with open(filename, "wb") as f:
            f.write(response.body)

    def parse(self, response):
        """解析网易云所有歌手"""
        datas = json.loads(response.body)
        artists = datas["artists"]
        for i, art in enumerate(artists):
            if i < 3:
                continue
            art_name = art["name"]
            art_info = {"art_name": art_name}
            artist_url = "https://music.163.com/artist/album?id=%s" % art["id"]
            yield scrapy.Request(artist_url, callback=self.parse_artist, headers=self.m_Heards, meta={"art_info": art_info})

    def parse_artist(self, response):
        """解析艺人歌手"""
        art_info = response.meta["art_info"]
        albums = response.xpath('//ul[@class="m-cvrlst m-cvrlst-alb4 f-cb"]/li')
        for album in albums:
            album_name = album.xpath('./div/@title').extract_first()
            suffix_url = album.xpath('./p/a/@href').extract_first()
            album_url = self.m_PrefixUrl + suffix_url
            album_info = copy.deepcopy(art_info)
            album_info["album_name"] = album_name
            yield scrapy.Request(album_url, callback=self.parse_album, headers=self.m_Heards, meta={"album_info": album_info})

        next_url = response.xpath('//div[@class="u-page"]/a[text()="下一页"]/@href').extract_first(None)
        if next_url and next_url.find("artist") != -1:
            yield response.follow(url=next_url, callback=self.parse_artist, headers=self.m_Heards, meta={"art_info": art_info})

    def parse_album(self, response):
        """解析艺人歌手专辑"""
        album_info = response.meta["album_info"]
        musics = response.xpath('//ul[@class="f-hide"]/li')
        for music in musics:
            music_name = music.xpath('./a/text()').extract_first()
            if music_name == "?":
                continue
            music_suffix_url = music.xpath('./a/@href').extract_first()
            music_id = music_suffix_url.split("=")[-1]

            art_name = self.re_fold(album_info["art_name"])
            album_name = self.re_fold(album_info["album_name"])
            music_name = self.re_fold(music_name)
            file_name = os.path.join(art_name, album_name, f"{art_name}-{music_name}")

            item = Music163Item()
            # item["art_name"] = album_info["art_name"]
            # item["album_name"] = album_info["album_name"]
            # item["music_name"] = music_name
            # file_name = f'{album_info["art_name"]}/{item["album_name"]}/{album_info["art_name"]}-{music_name}'
            item["music_id"] = music_id
            item["file_name"] = file_name
            yield item

            file_path = os.path.join(settings.FILES_STORE, file_name + ".lrc")
            if os.path.exists(file_path):
                continue
            lyric_url = "http://music.163.com/api/song/lyric?id={}&lv=1&kv=1&tv=-1".format(music_id)
            yield scrapy.Request(lyric_url, callback=self.parse_lyric, meta={"file_path": file_path})
            # v1?csrf_token=
            # music_url = self.m_PrefixUrl + music_suffix_url

    def parse_lyric(self, response):
        """解析歌词"""
        datas = json.loads(response.body)
        if "lrc" not in datas:
            return
        file_path = response.meta["file_path"]
        dir_path = os.path.split(file_path)[0]
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        lyric = datas["lrc"]["lyric"]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(lyric)
