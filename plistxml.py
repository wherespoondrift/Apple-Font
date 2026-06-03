import sys
import os
import plistlib
from humanfriendly import format_size, parse_size

currentFile = __file__
realPath = os.path.realpath(currentFile)
#dirPath = os.path.dirname(realPath)
#dirName = os.path.basename(dirPath)
# 指定目录路径
directory_path = os.path.dirname(realPath)


for filename in os.listdir(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.xml'):
            with open(filename, 'rb') as f:
                data = plistlib.load(f)
            output = filename.replace('.xml', '.md')
            with open(output, 'w', encoding='utf-8') as Flist:
                for FontInfo in data['Assets']:
                    FontInfo4 = FontInfo[ 'FontInfo4'][0]
                    if 'FontDesignLanguages' in FontInfo.keys():
                        FontDesignLang = FontInfo['FontDesignLanguages'][0]
                        if not len(FontInfo['FontDesignLanguages']) == 1:
                            FontDesignLang = 'en'
                    else:
                         FontDesignLang = 'en'
                    Flist.write(f'{FontInfo4[ 'FontFamilyName']} , {FontInfo4[ 'FontStyleName']}')
                    keys = list(FontInfo4['LocalizedFamilyNames'].keys())
                    keywords = ['en']
                    if not FontDesignLang in keys:
                        if len(keys)>1:
                            keys=[item for item in keys if item not in keywords]
                        FontDesignLang=keys[0]
                    Flist.write(f' , {FontInfo4['LocalizedFamilyNames'][FontDesignLang]}')
                    keys = list(FontInfo4['LocalizedStyleNames'].keys())
                    if not FontDesignLang in keys:
                        if len(keys)>1:
                            keys=[item for item in keys if item not in keywords]
                        FontDesignLang=keys[0]
                    Flist.write(f' , {FontInfo4['LocalizedStyleNames'][FontDesignLang]}')
                    if 'Prerequisite' in FontInfo.keys():
                        Flist.write(f' , {FontInfo[ 'Prerequisite'][0]}')
                    Flist.write(f' , {format_size(FontInfo[ '_UnarchivedSize'])} , {FontInfo[ '__BaseURL']}{FontInfo[ '__RelativePath']}')
                    Flist.write(f'\r\n')
