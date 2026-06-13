from fontTools.ttLib import TTFont, TTCollection, newTable
from fontTools.ttLib.tables._n_a_m_e import makeName, NameRecord
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from afdko import fdkutils
import opencc
import binascii
import sys, os, shutil
import struct
import re
import copy
import math
import time, traceback

currentFile = __file__
realPath = os.path.realpath(currentFile)
#dirPath = os.path.dirname(realPath)
#dirName = os.path.basename(dirPath)
current_dir = os.getcwd()
# 指定目录路径
directory_path = os.path.dirname(realPath)
if len(sys.argv) != 2 or sys.argv[1] not in ['otf', 'ttf', 'ttc']:
    print('\033[33m' + "用法: python convert_font.py otf/ttf/ttc        处理脚本所在目录的所有指定文件类型字体" + '\033[0m')
    sys.exit(1)

def checkfont(filename):
    command = "sfntedit -c  \"%s\" 2>&1" % (filename)
    report = fdkutils.runShellCmd(command)
    lines = report.split('\n')
    if "check failed" in report:
        print('\033[31m' + f"{report}" + '\033[0m')
        with open(filename, 'rb+') as file:
            content = file.read(1000)
            for line in lines:
                if "bad sfnt.rangeShift" in line:
                    x = re.findall(r"=(\w+)", line)
                    num=int(x[1])
                    fc="{:04x}".format(num)
                    file.seek(10)
                    file.write(binascii.unhexlify(fc))
                if "checksum" in line.lower():
                    m = re.findall(r"=(\w+)", line)
                    if len(m[0]) == 8:
                        offset = content.find(binascii.unhexlify(m[0]))
                        file.seek(offset)
                        file.write(binascii.unhexlify(m[1]))

intype = sys.argv[1]
t2s = opencc.OpenCC('t2s.json')
s2t = opencc.OpenCC('s2t.json')
if intype == 'ttc':
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.' + intype):
            print('\033[33m' + f"{fdkutils.runShellCmd("otc2otf -v  \"%s\" 2>&1" % (filename))}" + '\033[0m')
    sys.exit(1)
for filename in os.listdir(directory_path):
    file_path = os.path.join(directory_path, filename)
    if os.path.isfile(file_path) and filename.endswith('.' + intype):
    #if os.path.isfile(file_path) and filename.endswith('.' + intype) and filename.find("fixed") == -1:  # 检查文件扩展名
        print('\033[35m' + f"----- 处理文件 {filename} -----" + '\033[0m')
        filechage = 0
        #filename = 'STLibianTC-Regular.ttf'
        fixname = filename.replace('.', '_fixed.')
        font = TTFont(filename, recalcBBoxes=False, recalcTimestamp=False) #recalcBBoxes=False禁用自动重算边界框 recalcTimestamp=False
        #print(fdkutils.runShellCmd("tx -dump -0 \"%s\" 2>&1" % (filename)))
        #fdkutils.runShellCmd("sfntedit -d DSIG \"%s\" 2>&1" % (filename))
        #print('\033[36m' + f"{fdkutils.runShellCmd("spot -t name \"%s\" | awk 'BEGIN {flag=0} /LangTag\\[index\\]/ {flag=1} {if (!flag) print}' 2>&1" % (filename))} ", end="")
        #font['head'].__dict__
        #print('\033[33m' + f"{list(font.keys())}" + '\033[0m', end="")
        name_table = font['name']
        name_list = []
        for name in name_table.names:
            name_list.append(f"{name.platformID}-{name.nameID} {name.langID}")
        #print(f" {name_list}")
        for record in name_table.names:
            #print(f"name表:平台: {record.platformID}, 平台编码: {record.platEncID}, 编码: {record.getEncoding()}, 语言: {record.langID:>4}, 命名ID: {record.nameID:>2}, 描述: {record.toUnicode()}")
            if record.langID == 19:
                if "3-1 1028" not in name_list and "1-1 19" in name_list:
                    tc_record = NameRecord()
                    tc_record.nameID = record.nameID  # 使用一个自定义的 nameID，通常是256以上
                    tc_record.platformID = 3 # Windows平台
                    tc_record.platEncID =1  # Unicode平台编码ID
                    tc_record.langID = 1028  # 
                    tc_record.string = record.toUnicode().encode('utf-16-be')
                    name_table.names.append(tc_record)
                    filechage += 1
                    print('\033[33m' + f"\r添加Windows平台繁中 name {record.nameID}表, 描述: {record.toUnicode()}" + '\033[0m')
            if record.langID == 33:
                if "3-1 2052" not in name_list and "1-1 33" in name_list:
                    sc_record = NameRecord()
                    sc_record.nameID = record.nameID  # 使用一个自定义的 nameID，通常是256以上
                    sc_record.platformID = 3 # Windows平台
                    sc_record.platEncID =1  # Unicode平台编码ID
                    sc_record.langID = 2052  # 
                    sc_record.string = record.toUnicode().encode('utf-16-be')
                    name_table.names.append(sc_record)
                    filechage += 1
                    print('\033[33m' + f"\r添加Windows平台简中 name {record.nameID}表, 描述: {record.toUnicode()}" + '\033[0m')
            if record.langID == 11:
                if "3-1 1041" not in name_list and "1-1 11" in name_list:
                    sc_record = NameRecord()
                    sc_record.nameID = record.nameID  # 使用一个自定义的 nameID，通常是256以上
                    sc_record.platformID = 3 # Windows平台
                    sc_record.platEncID =1  # Unicode平台编码ID
                    sc_record.langID = 1041  # 
                    sc_record.string = record.toUnicode().encode('utf-16-be')
                    name_table.names.append(sc_record)
                    filechage += 1
                    print('\033[33m' + f"\r添加Windows平台日语 name {record.nameID}表, 描述: {record.toUnicode()}" + '\033[0m')
            if record.langID == 23:
                if "3-1 1042" not in name_list and "1-1 23" in name_list:
                    sc_record = NameRecord()
                    sc_record.nameID = record.nameID  # 使用一个自定义的 nameID，通常是256以上
                    sc_record.platformID = 3 # Windows平台
                    sc_record.platEncID =1  # Unicode平台编码ID
                    sc_record.langID = 1042  # 
                    sc_record.string = record.toUnicode().encode('utf-16-be')
                    name_table.names.append(sc_record)
                    filechage += 1
                    print('\033[33m' + f"\r添加Windows平台韩语 name {record.nameID}表, 描述: {record.toUnicode()}" + '\033[0m')
            if record.langID == 0:
                if not any("3-1" in elem for elem in name_list):
                    if record.nameID  <  100:
                        en_record = NameRecord()
                        en_record.nameID = record.nameID  # 使用一个自定义的 nameID，通常是256以上
                        en_record.platformID = 3 # Windows平台
                        en_record.platEncID =1  # Unicode平台编码ID
                        en_record.langID = 1033  # 
                        en_record.string = record.toUnicode().encode('utf-16-be')
                        name_table.names.append(en_record)
                        filechage += 1
                        print('\033[33m' + f"\r添加Windows平台英文 name {record.nameID}表, 描述: {record.toUnicode()}" + '\033[0m')
        print('\033[36m' + f"{fdkutils.runShellCmd("spot -t cmap \"%s\" | awk r'BEGIN {flag=0} /]=./ {flag=1} {if (!flag) print}' 2>&1" % (filename))} ", end="")
        #print('\033[36m' + f"{fdkutils.runShellCmd("spot -t cmap=11 \"%s\" 2>&1" % (filename))} ", end="")
        cmap_list = []
        cmap_table = font['cmap']
        for index, table in enumerate(cmap_table.tables):
            print('\033[33m' + f"\rcmap表>{index} 平台:{table.platformID} 平台编码:{table.platEncID:>2} 表格式:{table.format:>2} 编码:{table.getEncoding()} 字数:{len(table.cmap)} 表长:{table.length}" + '\033[0m')
            cmap_list.append(f"{table.platformID}-{table.platEncID}")
        #print(f"cmap{cmap_list}")
        print('\033[31m', end="")
        if '0-3' in cmap_list and '0-4' in cmap_list:
            if '3-1' not in cmap_list:
                table = cmap_table.getcmap(0, 3)
                new_subtable = CmapSubtable.newSubtable(table.format)
                new_subtable.cmap=table.cmap.copy()
                new_subtable.platformID = 3  # Microsoft
                new_subtable.platEncID = 1   # Unicode BMP (UCS-2)
                new_subtable.language = 0
                cmap_table.tables.append(new_subtable)
                filechage += 1
                print(f"\r复制为表3 1 cmap表>{cmap_table.tables.index(table)} {table.platformID} {table.platEncID} 表格式:{table.format} 编码:{table.getEncoding()} 字数:{len(table.cmap)} 表长:{table.length}")
            if '3-10' not in cmap_list:
                table = cmap_table.getcmap(0, 4)
                new_subtable = CmapSubtable.newSubtable(table.format)
                new_subtable.cmap=table.cmap.copy()
                new_subtable.platformID = 3  # Microsoft
                new_subtable.platEncID = 10   # Unicode BMP (UCS-2)
                new_subtable.language = 0
                cmap_table.tables.append(new_subtable)
                filechage += 1
                print(f"\r复制为表3 10 cmap表>{cmap_table.tables.index(table)} {table.platformID} {table.platEncID} 表格式:{table.format} 编码:{table.getEncoding()} 字数:{len(table.cmap)} 表长:{table.length}")
        elif cmap_table.tables[0].format==12 and cmap_table.tables[0].platformID==0:
            if '3-1' not in cmap_list:
                if '3-10' in cmap_list:
                    table = cmap_table.getcmap(3 , 10)
                else:
                    table = cmap_table.tables[0]
                new_subtable = CmapSubtable.newSubtable(4)
                new_subtable.platformID = 3
                new_subtable.platEncID = 1
                new_subtable.language = 0
                new_subtable.cmap={}
                for subtable in font['cmap'].tables:
                    if subtable.isUnicode():
                        for codepoint, name in subtable.cmap.items():
                            if codepoint <= 0xFFFF :
                                new_subtable.cmap[codepoint] = name
                cmap_table.tables.append(new_subtable)
                print(f"\r添加Windows平台3 1表 表格式:{new_subtable.format} 编码:{new_subtable.getEncoding()} 字数:{len(new_subtable.cmap)}") 
                filechage += 1
            if '3-10' not in cmap_list:
                table = cmap_table.tables[0]
                new_subtable = CmapSubtable.newSubtable(12)
                new_subtable.cmap=table.cmap.copy()
                new_subtable.platformID = 3  # Microsoft
                new_subtable.platEncID = 10   # Unicode BMP (UCS-2)
                new_subtable.language = 0
                cmap_table.tables.append(new_subtable)
                filechage += 1
                print(f"\r复制为表3 10 cmap表>{cmap_table.tables.index(table)} {table.platformID} {table.platEncID} 表格式:{table.format} 编码:{table.getEncoding()} 字数:{len(table.cmap)} 表长:{table.length}")
        elif '3-1' not in cmap_list:
            if '3-10' not in cmap_list:
                if '0-4' in cmap_list:
                    table = cmap_table.getcmap(0, 4)
                elif '0-3' in cmap_list and cmap_table.getcmap(0, 3).format==12:
                    table = cmap_table.getcmap(0, 3)
                    #table.platEncID = 4
                new_subtable = CmapSubtable.newSubtable(12)
                new_subtable.cmap=table.cmap.copy()
                new_subtable.platformID = 3  # Microsoft
                new_subtable.platEncID = 10   # Unicode BMP (UCS-2)
                new_subtable.language = 0
                cmap_table.tables.append(new_subtable)
                filechage += 1
                print(f"\r复制为表3 10 cmap表>{cmap_table.tables.index(table)} {table.platformID} {table.platEncID} 表格式:{table.format} 编码:{table.getEncoding()} 字数:{len(table.cmap)} 表长:{table.length}")
            # 创建新的 cmap_format_4 子表
            new_subtable = CmapSubtable.newSubtable(4)
            new_subtable.platformID = 3  # Microsoft
            new_subtable.platEncID = 1   # Unicode BMP (UCS-2)
            new_subtable.language = 0
            new_subtable.cmap = {}
            # 合并所有 Unicode 子表的映射到新的子表中，过滤掉码位大于 0xFFFF 的字符
            for subtable in font['cmap'].tables:
                if subtable.isUnicode():
                    for codepoint, name in subtable.cmap.items():
                        if codepoint <= 0xFFFF :
                            new_subtable.cmap[codepoint] = name
            cmap_table.tables.append(new_subtable)
            print(f"已添加 cmap_format_4 子表 字数 {len(new_subtable.cmap)} 提高 Windows 兼容性。")
            filechage += 1
        for index, table in enumerate(cmap_table.tables):
            if not (table.platformID == 1 and table.platEncID == 0) and table.format == 2 and '3-1' not in cmap_list:
                print('\033[33m' + f"\rcmap表>{index} 平台:{table.platformID} 平台编码:{table.platEncID:>2} 表格式:{table.format:>2} 编码:{table.getEncoding()} 字数:{len(table.cmap)}" + '\033[0m')
                new_subtable = CmapSubtable.newSubtable(12)
                new_subtable.platformID = table.platformID
                new_subtable.platEncID = table.platEncID
                new_subtable.language = table.language
                new_subtable.cmap=table.cmap.copy()
                #new_subtable.cmap = {}
                #valid_glyph_names = set(font.getGlyphOrder())
                #for codepoint, glyphName in table.cmap.items():
                    #if not isinstance(glyphName, str):
                        #glyphName = str(glyphName)
                        #print(f"字形名称非字符串，已转换为字符串：{glyphName}")
                    #if glyphName in valid_glyph_names:
                        #new_subtable.cmap[codepoint] = glyphName
                cmap_table.tables.remove(table)
                cmap_table.tables.append(new_subtable)
                filechage += 1
                print('\033[31m' + f"\r格式2表>{cmap_table.tables.index(new_subtable)}转格式12 平台:{new_subtable.platformID} 平台编码:{new_subtable.platEncID:>2} 编码:{new_subtable.getEncoding()} 字数:{len(new_subtable.cmap)}" + '\033[0m')
            else:
                pass
        print('\033[0m', end="")
        #print("Family Name:", font['name'].getBestFamilyName())  # 如 "HarmonyOS Sans"
        #print("Full Name:", font['name'].getBestFullName())
        print('\033[33m' + "默认名称:", name_table.getDebugName(4))
        print('\033[33m' + "默认版本:", name_table.getDebugName(5))
        print('\033[33m' + "默认PostScript:", name_table.getDebugName(6))
        print("Family:", name_table.getName(1, 3, 1, 2052)) 
        print("Style:", name_table.getName(2, 3, 1, 2052))
        print("Full:", name_table.getName(4, 3, 1, 2052), '\033[0m')
        #print(dir( font ), "\n")
        #font.save(output)
        #print(f"Converted {filename} to {output}")
        #font.saveXML(filename[:-4] +".xml")
        command = "sfntedit -c  \"%s\" 2>&1" % (filename)
        report = fdkutils.runShellCmd(command)
        if not filechage == 0:
            try:
                #if not os.path.exists(fixname):
                if os.path.exists(filename):
                    font.save(filename)
                    font.close()
                    print('\033[33m' + f"{filename} 修改已保存\n" + '\033[0m')
                else:
                    print('\033[32m' + f"{fixname} 已存在  \n" + '\033[0m')
            except Exception as e:
                print('\033[31m' + f"{filename} 保存出错，建议从其他来源找字体{name_table.getDebugName(6)}\n" + '\033[0m', traceback.format_exc())
        elif "failed" in report:
            checkfont(filename)
            checkfont(filename)
            checkfont(filename)
            print('\033[33m' + f"{filename} 文件校验已修正." + '\033[0m')
        else:
            print('\033[32m' + f"字体 {filename} 兼容windows不作改动。\n" + '\033[0m')
        #font.save(filename)
        #print(f" { font['name'].names}")

#   ttx -t cmap PingFangHK-Light.otf
#   ttx -t name PingFangHK-Light.otf
#   sfntedit -c WawaSC-Regular.otf
#   spot -tcmap=11 WawaSC-Regular.otf
#   sed -i '''s/platformID="0" platEncID="3"/platformID="3" platEncID="1"/g' PingFangHK-Light.ttx
#   sed -i '''s/platformID="0" platEncID="4"/platformID="3" platEncID="10"/g' PingFangHK-Light.ttx
#   ttx --no-recalc-timestamp -b -m PingFangHK-Light.otf PingFangHK-Light.ttx
#   禁用自动重算边界框：TTFont("font.ttf", recalcBBoxes=False) 或命令行加 -b 标志（如 ttx -b font.ttf）
########################################################################################################################
#for file in *tf ; do  echo -e "\033[33m--- $file ---\033[0m";spot -t name $file | awk 'BEGIN {flag=0} /LangTag\[index\]=/ {flag=1} {if (!flag) print}';spot -tcmap=11 $file;spot -t cmap $file | awk 'BEGIN {flag=0} /\]=./ {flag=1} {if (!flag) print}';done
#for file in *tf ; do  echo -e "\033[33m--- $file ---\033[0m";sfntedit -c $file;spot -T $file ;spot -tcmap=11 $file;spot -t cmap $file | awk 'BEGIN {flag=0} /\]=./ {flag=1} {if (!flag) print}';done
#for file in *tf ; do  echo -e "\033[33m--- $file ---";echo -ne "`sfntedit -c $file`\033[0m";spot -tcmap=11 $file;spot -t cmap $file | awk 'BEGIN {flag=0} /\]=./ {flag=1} {if (!flag) print}';done
#font.saveXML("temp2.xml",tables=["name"])