from fontTools.ttLib import TTFont, TTCollection
import json
import sys, os, shutil, re
 
if len(sys.argv) != 2 or all(x not in sys.argv[1] for x in  ['otf', 'ttf', 'ttc']):
    print('\033[33m' + "用法: python fontcmap.py fontname 生成字符映射表json" + '\033[0m')
    sys.exit(1)

fontName = sys.argv[1]
dic = {}
font = TTFont(fontName, fontNumber=0)
glyphNames = font.getGlyphNames()

for subtable in font['cmap'].tables:
    if subtable.isUnicode():
        for codepoint, name in subtable.cmap.items():
            dic[name] = chr(codepoint)

dic['字符总数'] = len(dic.keys())
last_item = list(dic.items())[-1]  # 获取最后一个项作为元组 (key, value)
d_items = [last_item] + list(dic.items())[:-1]# 将最后一项移到列表的第一位
dic = dict(d_items)  # 将列表的元组转换回字典

with open(f"{fontName[:-4]}.json", "w",) as json_file:
    json.dump(dic, json_file, ensure_ascii=False)