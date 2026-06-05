from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
import opencc
import sys
import os
import shutil
from afdko import fdkutils
import struct
import re
import copy
import math
import time
import binascii

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
    if os.path.isfile(file_path) and filename.endswith('.' + intype):  # 检查文件扩展名
        print('\033[32m' + f"处理文件 {filename}  . . ." + '\033[0m')
        filechage = 0
        if  intype == 'otf':
            output = filename.replace('.otf', '.ttf')
        elif intype == 'ttf':
            output = filename.replace('.ttf', '.otf')
        fixname = filename.replace('.', 'fix.')
        #filename = 'PingFangHK-Light.otf'
        #print(fdkutils.runShellCmd("tx -dump -0 \"%s\" 2>&1" % (filename)))
        #fdkutils.runShellCmd("sfntedit -d DSIG \"%s\" 2>&1" % (filename)))
        command = "sfntedit -c  \"%s\" 2>&1" % (filename)
        report = fdkutils.runShellCmd(command)
        if "failed" in report:
            checkfont(filename)
            checkfont(filename)
            checkfont(filename)
            print('\033[33m' + f"{filename} 文件校验已修正." + '\033[0m')
        else:
            print('\033[33m' + f"{filename} 文件校验\"通过\"." + '\033[0m')
        font = TTFont(filename, recalcTimestamp=False, recalcBBoxes=False) #禁用自动重算边界框
        name_table = font['name']
        #print('\033[36m' + f"{fdkutils.runShellCmd("spot -t name \"%s\" | awk 'BEGIN {flag=0} /LangTag\\[index\\]/ {flag=1} {if (!flag) print}' 2>&1" % (filename))} ", end="")
        #print(dir( name_table ), "\n")
        #print(f" {name_table.names}")
        #list(font.keys())
        #print('\033[33m' + f"{font.keys()}" + '\033[36m', end="")
        name_list = []
        for name in name_table.names:
            name_list.append(f"{name.platformID}-{name.nameID} {name.langID}")
        #print(f" {name_list}")
        for record in name_table.names:
            #print(f"name表:平台: {record.platformID}, 平台编码: {record.platEncID}, 编码: {record.getEncoding()}, 语言: {record.langID:>4}, 命名ID: {record.nameID:>2}, 描述: {record.toUnicode()}")
            #if record.nameID == 1 and record.platformID == 3:
                #print(f"--PlatformID: {record.platformID}, EncodingID: {record.platEncID}, LanguageID: {record.langID}, NameID: {record.nameID}, String: {record.toUnicode()}")
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
                    print('\033[33m' + f"添加Windows平台繁中 name {record.nameID}表" + '\033[0m')
                if "x3-1 2052" in name_list:
                    sc_record = NameRecord()
                    sc_record.nameID = record.nameID  # 使用一个自定义的 nameID，通常是256以上
                    sc_record.platformID = 3 # Windows平台
                    sc_record.platEncID =1  # Unicode平台编码ID
                    sc_record.langID = 2052  # 
                    sc_record.string = t2s.convert(record.toUnicode()).encode('utf-16-be')
                    name_table.names.append(sc_record)
                    filechage += 1
                    print('\033[33m' + f"添加Windows平台繁中 name {record.nameID}表转简中" + '\033[0m')
            if record.langID == 33:
                if "x3-1 1028" in name_list:
                    tc_record = NameRecord()
                    tc_record.nameID = record.nameID  # 使用一个自定义的 nameID，通常是256以上
                    tc_record.platformID = 3 # Windows平台
                    tc_record.platEncID =1  # Unicode平台编码ID
                    tc_record.langID = 1028  # 
                    tc_record.string = s2t.convert(record.toUnicode()).encode('utf-16-be')
                    name_table.names.append(tc_record)
                    filechage += 1
                    print('\033[33m' + f"添加Windows平台简中 name {record.nameID}表转繁中" + '\033[0m')
                if "3-1 2052" not in name_list and "1-1 33" in name_list:
                    sc_record = NameRecord()
                    sc_record.nameID = record.nameID  # 使用一个自定义的 nameID，通常是256以上
                    sc_record.platformID = 3 # Windows平台
                    sc_record.platEncID =1  # Unicode平台编码ID
                    sc_record.langID = 2052  # 
                    sc_record.string = record.toUnicode().encode('utf-16-be')
                    name_table.names.append(sc_record)
                    filechage += 1
                    print('\033[33m' + f"添加Windows平台简中 name {record.nameID}表" + '\033[0m')
            if record.langID == 0:
                if not any("3-1" in elem for elem in name_list):
                    if record.nameID  <  20:
                        en_record = NameRecord()
                        en_record.nameID = record.nameID  # 使用一个自定义的 nameID，通常是256以上
                        en_record.platformID = 3 # Windows平台
                        en_record.platEncID =1  # Unicode平台编码ID
                        en_record.langID = 1033  # 
                        en_record.string = record.toUnicode().encode('utf-16-be')
                        name_table.names.append(en_record)
                        filechage += 1
                        print('\033[33m' + f"添加Windows平台英文 name {record.nameID}表" + '\033[0m')
        cmap_list = []
        print('\033[36m' + f"{fdkutils.runShellCmd("spot -t cmap \"%s\" | awk r'BEGIN {flag=0} /]=./ {flag=1} {if (!flag) print}' 2>&1" % (filename))} ", end="")
        #print('\033[36m' + f"{fdkutils.runShellCmd("spot -t cmap=11 \"%s\" 2>&1" % (filename))} ", end="")
        tables = font['cmap'].tables
        for index, table in enumerate(tables):
           print('\033[33m' + f"\rcmap表{index} 平台:{table.platformID} 平台编码:{table.platEncID:>2} 表格式:{table.format:>2} 编码:{table.getEncoding()} 表长:{table.length}" + '\033[0m')
           cmap_list.append(f"{table.platformID}-{table.platEncID}")
        #print(f"cmap{cmap_list}")
        if any("3-" in elem for elem in cmap_list):
            print('\033[36m' + f"字体兼容Windows平台", '\033[0m')
        else:
            print('\033[36m' + f"字体无Windows平台数据", '\033[0m')
        print('\033[31m', end="")
        force = 0
        if '0-3' in cmap_list and '0-4' in cmap_list:
            if '3-1' not in cmap_list:
                table = font['cmap'].getcmap(0, 3)
                table.platformID  = 3
                table.platEncID  = 1
                filechage += 1
                print(f"修改 0 3 cmap 表{font['cmap'].tables.index(table)} 改为 {table.platformID} {table.platEncID:>2} 表格式:{table.format:>2} 编码:{table.getEncoding()} 表长:{table.length}")
            if '3-10' not in cmap_list:
                table = font['cmap'].getcmap(0, 4)
                table.platformID  = 3
                table.platEncID  = 10
                filechage += 1
                print(f"修改 0 4 cmap 表{font['cmap'].tables.index(table)} 改为 {table.platformID} {table.platEncID:>2} 表格式:{table.format:>2} 编码:{table.getEncoding()} 表长:{table.length}")
        if '0-3' in cmap_list and '0-4' not in cmap_list:
            if '3-1' not in cmap_list:
                table = font['cmap'].getcmap(0, 3)
                if font['cmap'].tables.index(table)==0:
                    table.platformID  = 3
                    table.platEncID  = 1
                    filechage += 1
                    #shutil.copyfile(filename, filename + '.' + time.strftime("%M%S"))
                    print(f"尝试修改 cmap 表{font['cmap'].tables.index(table)} 改为 {table.platformID} {table.platEncID:>2} 表格式:{table.format:>2} 编码:{table.getEncoding()} 表长:{table.length}")
        if 'x0-4' in cmap_list and '0-3' not in cmap_list:
            if '3-1' not in cmap_list and '3-10' not in cmap_list:
                table = font['cmap'].getcmap(0,4)
                if font['cmap'].tables.index(table)==0:
                    table.platformID  = 0
                    table.platEncID  = 3
                    filechage += 1
                    #shutil.copyfile(filename, filename + '.' + time.strftime("%M%S"))
                    print(f"尝试修改 cmap 表{font['cmap'].tables.index(table)} 改为 {table.platformID} {table.platEncID:>2} 表格式:{table.format:>2} 编码:{table.getEncoding()} 表长:{table.length}")
        if 'x3-10' in cmap_list:
            if '0-4' not in cmap_list:
                if '1-1' in cmap_list:
                    table = font['cmap'].getcmap(1, 1)
                    table.platformID  = 3
                    table.platEncID  = 2
                    filechage += 1
                    print(f"修改 1 1 japanese cmap 改为 {table.platformID} {table.platEncID} 表格式:{table.format:>2} 编码:{table.getEncoding()} 表长:{table.length}")
                if '1-2' in cmap_list:
                    table = font['cmap'].getcmap(1, 2)
                    table.platformID  = 3
                    table.platEncID  = 4
                    filechage += 1
                    print(f"修改 1 2 trad_chinese cmap 改为 {table.platformID} {table.platEncID} 表格式:{table.format:>2} 编码:{table.getEncoding()} 表长:{table.length}")
                if '1-3' in cmap_list:
                    table = font['cmap'].getcmap(1, 3)
                    table.platformID  = 3
                    table.platEncID  = 5
                    filechage += 1
                    print(f"修改 1 3 korean cmap 改为 {table.platformID} {table.platEncID} 表格式:{table.format:>2} 编码:{table.getEncoding()} 表长:{table.length}")
                if '1-25' in cmap_list:
                    table = font['cmap'].getcmap(1, 25)
                    table.platformID  = 3
                    table.platEncID  = 3
                    filechage += 1
                    print(f"修改 1 25 simp_chinese cmap改为 {table.platformID} {table.platEncID} 表格式:{table.format:>2} 编码:{table.getEncoding()} 表长:{table.length}")
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
        #print(f"文件状态 {filechage}")
        if filechage != 0:
            font.save(fixname)
            print('\033[33m' + f"{filename} table 修改已保存\n" + '\033[0m')
        else:
            print('\033[33m' + f"{filename} table 不作改动。\n" + '\033[0m')
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
#from fontTools.ttLib import TTFont
#import fontTools.merge as merge
 
# 加载字体并保留原始时间戳
#font1 = TTFont("font1.ttf", recalcTimestamp=False, recalcBBoxes=False)
#font2 = TTFont("font2.ttf", recalcTimestamp=False, recalcBBoxes=False)
 
# 合并字体
#merger = merge.Merger()
#merged_font = merger.merge([font1, font2])
 
# 保存合并结果，保持时间戳
#merged_font.save("merged.ttf")