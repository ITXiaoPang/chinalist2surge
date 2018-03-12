#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import getpass
import requests

__author__ = "ITXiaoPang"
__mtime__ = "2018/3/10"


url_accelerated_domains =\
    "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/accelerated-domains.china.conf"
url_apple_domains = "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/apple.china.conf"
url_google_domains = "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/google.china.conf"

url_china_lists = (url_accelerated_domains, url_apple_domains, url_google_domains)
ChinaList_file = "/tmp/ChinaList.txt"

reg_china_list = ".*/(.+)/.*"


curr_user = getpass.getuser()
# surge_conf_path = f"/Users/{curr_user}/Library/Mobile Documents/iCloud~run~surge/Documents/"
surge_conf_path = f"/Users/{curr_user}/Syncthing/Settings/Surge/"
surge_template = f"{surge_conf_path}Surge.conf"
surge_policy = "🚀中国加速"
surge_flag_start = "//white_list_start"
surge_flag_end = "//white_list_end"
surge_gfw_conf = f"{surge_conf_path}ChinaList.conf"


if __name__ == "__main__":
    if not os.path.exists(surge_template):
        print(f"模板文件未找到：{surge_template}")
        exit()

    print("开始更新缓存")
    list_text = ''
    for curr_list_url in url_china_lists:
        print(f"读取{curr_list_url}")
        try:
            my_response = requests.get(curr_list_url)
            if my_response.status_code == requests.codes.ok:
                list_text = ''.join([list_text, my_response.text])
            else:
                print(f'读取失败:{my_response.status_code}，跳过该规则')
        except Exception as ex:
            print(ex)
            continue

    print(f"写入文件{ChinaList_file}")
    try:
        with open(ChinaList_file, mode="w", encoding="utf-8") as f_gfw_list:
            f_gfw_list.write(list_text)
    except IOError as ex:
        print(f"缓存更新失败，错误：{ex}")
    else:
        print(f"缓存更新成功:{ChinaList_file}")


    if os.path.exists(ChinaList_file):
        print(f"读取文件{ChinaList_file}")
        try:
            white_list = []
            black_list = []
            with open(ChinaList_file, mode="r", encoding="utf-8") as f_gfw_list:
                comment = re.compile(reg_china_list)
                white_list = comment.findall(f_gfw_list.read())

            white_list_text = ""
            for curr_url in white_list:
                white_list_text += f"DOMAIN-SUFFIX,{curr_url},{surge_policy}{os.linesep}"

            # 增加flag
            white_list_text = "".join(
                [
                    surge_flag_start, os.linesep,
                    white_list_text, os.linesep,
                    surge_flag_end
                ]
            )

            if os.path.exists(surge_template):
                try:
                    print(f"读取模板{surge_template}")
                    with open(surge_template, mode="r", encoding="utf-8") as f_surge_template:
                        surge_template_text = f_surge_template.read()
                    comment = re.compile(f"{surge_flag_start}(.*?){surge_flag_end}", re.DOTALL)
                    if comment.findall(surge_template_text):
                        result, number = comment.subn(white_list_text, surge_template_text)
                        print(f"写入规则文件{surge_gfw_conf}")
                        with open(surge_gfw_conf, mode="w", encoding="utf-8") as f_surge_gfw_conf:
                            f_surge_gfw_conf.write(result)
                    else:
                        raise ModuleNotFoundError
                except IOError as ex:
                    print(f"规则写入失败，错误：{ex}")
                except ModuleNotFoundError:
                    print(f"未找到指定标记{surge_flag_start}和{surge_flag_end}")
                else:
                    print("规则写入成功")
        except IOError as ex:
            print(f"白名单缓存读取失败，错误：{ex}")
    else:
        print(f"文件{ChinaList_file}不存在。")
