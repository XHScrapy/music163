# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines import files

from .items import Music163Item


class Music163Pipeline(files.FilesPipeline):

    m_MusicUrl = "http://music.163.com/song/media/outer/url?id={}.mp3"

    def get_media_requests(self, item, info):
        if not isinstance(item, Music163Item):
            return
        music_id = item["music_id"]
        music_url = self.m_MusicUrl.format(music_id)
        yield scrapy.Request(music_url, meta={"item": item})

    def file_path(self, request, response=None, info=None):
        item = request.meta["item"]
        music_suf = request.url.split(".")[-1]
        filename = item["file_name"] + "." + music_suf
        return filename

    def item_completed(self, results, item, info):
        music_paths = [x['path'] for ok, x in results if ok]
        if not music_paths:
            raise DropItem("Item contains no files")
        return item
