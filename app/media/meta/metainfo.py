import os.path
import re

from app.media.meta.metaanime import MetaAnime
from app.media.meta.metavideo import MetaVideo
from app.utils.types import MediaType
from config import RMT_MEDIAEXT, Config


def MetaInfo(title, subtitle=None, mtype=None):
    """
    媒体整理入口，根据名称和副标题，判断是哪种类型的识别，返回对应对象
    :param title: 标题、种子名、文件名
    :param subtitle: 副标题、描述
    :param mtype: 指定识别类型，为空则自动识别类型
    :return: MetaAnime、MetaVideo
    """
    config = Config()
    # 应用屏蔽词
    used_ignored_words = []
    # 应用替换词
    used_replaced_words = []
    # 应用集数偏移
    used_offset_words = []
    # 屏蔽词
    ignored_words = config.get_config('laboratory').get("ignored_words")
    if ignored_words:
        ignored_words = re.sub(r"\|\|", '|', ignored_words)
        ignored_words = re.compile(r'' + ignored_words)
        # 去重
        used_ignored_words = list(set(re.findall(ignored_words, title)))
        if used_ignored_words:
            title = re.sub(ignored_words, '', title)
    # 替换词
    replaced_words = config.get_config('laboratory').get("replaced_words")
    if replaced_words:
        replaced_words = replaced_words.split("||")
        for replaced_word in replaced_words:
            if not replaced_word:
                continue
            replaced_word_info = replaced_word.split("@")
            if re.findall(r'' + replaced_word_info[0], title):
                used_replaced_words.append(replaced_word)
                title = re.sub(r'' + replaced_word_info[0], r'' + replaced_word_info[-1], title)
    # 集数偏移
    offset_words = config.get_config('laboratory').get("offset_words")
    if offset_words:
        offset_words = offset_words.split("||")
        for offset_word in offset_words:
            if not offset_word:
                continue
            offset_word_info = offset_word.split("@")
            try:
                offset_num = int(offset_word_info[2])
                offset_word_info_re = re.compile(r'' + "(?<=%s)[0-9]+(?=%s)"%(offset_word_info[0], offset_word_info[1]))
                episode_num = re.findall(offset_word_info_re, title)
                if not episode_num:
                    continue
                episode_num = int(episode_num[0])
                used_offset_words.append(offset_word)
                title = re.sub(offset_word_info_re, r'' + str(episode_num + offset_num).zfill(2), title)
            except Exception as err:
                print(err)
    # 判断是否处理文件
    if title and os.path.splitext(title)[-1] in RMT_MEDIAEXT:
        fileflag = True
    else:
        fileflag = False
    if mtype == MediaType.ANIME or is_anime(title):
        meta_info = MetaAnime(title, subtitle, fileflag)
        meta_info.ignored_words = used_ignored_words
        meta_info.replaced_words = used_replaced_words
        meta_info.offset_words = used_offset_words
        return meta_info
    else:
        meta_info = MetaVideo(title, subtitle, fileflag)
        meta_info.ignored_words = used_ignored_words
        meta_info.replaced_words = used_replaced_words
        meta_info.offset_words = used_offset_words
        return meta_info


def is_anime(name):
    """
    判断是否为动漫
    :param name: 名称
    :return: 是否动漫
    """
    if not name:
        return False
    if re.search(r'【[+0-9XVPI-]+】\s*【', name, re.IGNORECASE):
        return True
    if re.search(r'\s+-\s+[\dv]{1,4}\s+', name, re.IGNORECASE):
        return True
    if re.search(r"S\d{2}\s*-\s*S\d{2}|S\d{2}|\s+S\d{1,2}|EP?\d{2,4}\s*-\s*EP?\d{2,4}|EP?\d{2,4}|\s+EP?\d{1,4}", name,
                 re.IGNORECASE):
        return False
    if re.search(r'\[[+0-9XVPI-]+]\s*\[', name, re.IGNORECASE):
        return True
    return False
