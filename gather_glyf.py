from fontTools.ttLib import TTCollection, TTFont, TTLibError, newTable
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates, GlyphComponent
import sys, os, shutil
from afdko import fdkutils

def update_hmtx(ttFont, glyf):
    hmtx = ttFont['hmtx']
    for glyphName, glyph in glyf.glyphs.items():
        if hasattr(glyph, 'xMin'):
            hmtx[glyphName] = (hmtx[glyphName][0], glyph.xMin)

if len(sys.argv) != 3:
    print('\033[33m' + "用法: python gather_glyf.py font1 font2 将font2中font1没有的字形收集写入font1" + '\033[0m')
    sys.exit(1)
# fdkutils.runShellCmd("sfntedit -d DSIG \"%s\" 2>&1" % (sys.argv[1]))
# 加载字体文件
#font = TTFont('STLibianSC-Regular.ttf')
#font2 = TTFont('STLibianTC-Regular.ttf')
#font = TTFont(sys.argv[1], recalcBBoxes=False, recalcTimestamp=False)
#font2 = TTFont(sys.argv[2], recalcBBoxes=False, recalcTimestamp=False)
font = TTFont(sys.argv[1], recalcBBoxes=False, recalcTimestamp=False)
font2 = TTFont(sys.argv[2], recalcTimestamp=False)

for index, table in enumerate(font['cmap'].tables):
    print('\033[32m' + f"\rcmap表>{index} 平台:{table.platformID} 平台编码:{table.platEncID:>2} 表格式:{table.format:>2} 编码:{table.getEncoding()} 字数:{len(table.cmap)}" + '\033[0m')

cmapPreferences=(
    (3, 10),
    (0, 6),
    (0, 4),
    (3, 1),
    (0, 3),
    (0, 2),
    (0, 1),
    (0, 0),
)

for platformID, platEncID in cmapPreferences:
    cmapSubtable = font['cmap'].getcmap(platformID, platEncID)
    if cmapSubtable is not None and cmapSubtable.format>=12:
        BestCmap = font['cmap'].getcmap(platformID, platEncID)
    else:
        newSubtable = font['cmap'].tables[0].newSubtable(12)
        newSubtable.platformID = 3
        newSubtable.platEncID = 10
        newSubtable.language  = 0
        newSubtable.cmap = {}
        for subtable in font['cmap'].tables:
            if subtable.isUnicode():
                for codepoint, name in subtable.cmap.items():
                    newSubtable.cmap[codepoint] = name
        font['cmap'].tables.append(newSubtable)
        BestCmap = font['cmap'].getcmap(3, 10)
        print('\033[33m' + f"创建 cmap_format_12 3-10 window平台映射表 字数:{len(BestCmap.cmap)}" + '\033[0m')
    break

#for platformID, platEncID in cmapPreferences:
#    cmapSubtable = font2['cmap'].getcmap(platformID, platEncID)
#    if cmapSubtable is not None:
#        BestCmap2 = font2['cmap'].getcmap(platformID, platEncID)

allcmp= {}
allcmp2= {}
trCmap = {}
trCmap2 = {}

for subtable in font['cmap'].tables:
    if subtable.isUnicode():
        for codepoint, name in subtable.cmap.items():
             trCmap[name] = codepoint

for subtable in font2['cmap'].tables:
    if subtable.isUnicode():
        for codepoint, name in subtable.cmap.items():
             trCmap2[name] = codepoint

for subtable in font['cmap'].tables:
    if subtable.isUnicode():
        for codepoint, name in subtable.cmap.items():
            allcmp.setdefault(codepoint, set()).add(name)

#len(allcmp)

#allcmp2={}
#for subtable in font2['cmap'].tables:
#    if subtable.isUnicode():
#        for codepoint, name in subtable.cmap.items():
#            allcmp2.setdefault(codepoint, set()).add(name)

#len(allcmp2)

items={}
for subtable in font['cmap'].tables:
    if subtable.isUnicode():
        items = list(items) + list(subtable.cmap)

itls = set(items)
#len(itls)

#reCmap = font['cmap'].buildReversed()
#reCmap2 = font2['cmap'].buildReversed()

if font['cmap'].getcmap(3, 1) is not None:
    cmap31 = font['cmap'].getcmap(3, 1)
else:
    newSubtable = font['cmap'].tables[0].newSubtable(4)
    newSubtable.platformID = 3
    newSubtable.platEncID = 1
    newSubtable.language = 0
    newSubtable.cmap = {}
    for subtable in font['cmap'].tables:
        if subtable.isUnicode():
            for codepoint, name in subtable.cmap.items():
                if codepoint <= 0xFFFF :
                    newSubtable.cmap[codepoint] = name
    font['cmap'].tables.append(newSubtable)
    cmap31 = font['cmap'].getcmap(3, 1)
    print('\033[33m' + f"添加 cmap_format_4 3-1 window平台映射表 字数:{len(cmap31.cmap)}" + '\033[0m')

seen_glyphs = set(font['glyf'].glyphs.keys())
cmap_pname = set(trCmap.keys())
cmap_pname2 = set(trCmap2.keys())

for glyph_name, glyph_data in font['glyf'].glyphs.items():
     if glyph_name not in cmap_pname and glyph_name.upper().startswith('UNI') and '.' not in glyph_name:
         print('\033[33m' + f"{sys.argv[1]} 发现未映射uni字形 {glyph_name}" + '\033[0m')

for glyph_name, glyph_data in font2['glyf'].glyphs.items():
     if glyph_name not in cmap_pname2 and glyph_name.upper().startswith('UNI') and '.' not in glyph_name:
         print('\033[33m' + f"{sys.argv[2]} 发现未映射uni字形 {glyph_name} " + '\033[0m')

#os.system('clear')
ch = 0
print('\033[33m' + f"{sys.argv[1]}字形数：{font['maxp'].numGlyphs }" + '\033[0m')
#for codepoint, glyph_name in allcmp2.items():
for subtable in font2['cmap'].tables:
    if subtable.isUnicode():
        for codepoint, glyph_name in subtable.cmap.items():
            if codepoint not in BestCmap.cmap.keys():
            #if codepoint not in itls:
           # if glyph_name not in cmap_pname:
                if codepoint <= 0xFFFF :
                    if codepoint not in cmap31.cmap.keys():
                        cmap31.cmap[codepoint] = glyph_name
                        #print('\033[33m' + f"添加 {"{:0x}".format(codepoint)}  {glyph_name} 到 camp 3-1 映射表" + '\033[0m')
                if codepoint not in BestCmap.cmap.keys():
                    BestCmap.cmap[codepoint] = glyph_name
                    print('\033[33m' + f"添加 {"{:0x}".format(codepoint).upper()}  {glyph_name} 到 camp 3-10 映射表" + '\033[0m')
                    if codepoint not in allcmp.keys():
                        if glyph_name in seen_glyphs:
                            name = "uid{:0x}".format(codepoint)
                            if name in seen_glyphs:
                                raise TTLibError(f'{glyph_name} 和 {name} 都在没有映射 {"{:0x}".format(codepoint)} ？')
                        else:
                            name = glyph_name
                    #if glyph_name not in seen_glyphs and glyph_name not in cmap_pname:
                            ch += 1
                            glyph = font2['glyf'][glyph_name]
                            font['glyf'].glyphs[name] = glyph
                            #font['maxp'].numGlyphs += 1  # 更新最大字形数
                            font['glyf'].glyphOrder.append(name)
                            print('\033[32m' + f"添加 {"{:0x}".format(codepoint).upper()} {name} 字形到glyf表 " + '\033[0m')
                            #if hasattr(glyph, 'xMin'):
                            font["hmtx"][name] = font2["hmtx"][glyph_name]
                            try:
                                font["vmtx"][name] = font2["vmtx"][glyph_name]
                            except:
                                pass

font['maxp'].numGlyphs = len(set(font['glyf'].glyphs.keys()))
if  ch == 9999:
    for name in font['glyf'].keys():
        glyph = font['glyf'][name]
        if hasattr(glyph, 'xMin'):
            #font["hmtx"][name] = (font["hmtx"][name][0], glyph.xMin)
            pass
        else:
            #print('\033[32m' + f" {name} 非标准字形" + '\033[0m')
            font["hmtx"][name] = (font["hmtx"][name][0], int(60))

# 更新maxp表的numGlyphs字段（如果需要）
#font['maxp'].numGlyphs = len(font['glyf'].glyphs)
print('\033[33m' + f"合成后字形数：{len(font['glyf'].glyphs)}" + '\033[0m')
for index, table in enumerate(font['cmap'].tables):
    print('\033[33m' + f"\rcmap表>{index} 平台:{table.platformID} 平台编码:{table.platEncID:>2} 表格式:{table.format:>2} 编码:{table.getEncoding()} 字数:{len(table.cmap)}" + '\033[0m')

# 保存新的字体文件
#font.save(sys.argv[1][:-4]+"_mix.ttf")
font.save(sys.argv[1])
