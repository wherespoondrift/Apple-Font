# Apple-Font
下载plist xml文件和py脚本放同一目录运行plistxml.py得到如下方便浏览文本

Apple LiSung , Light , 蘋果儷細宋 , 細宋 , CJK , 8.97 MB , http://updates-http.cdn-apple.com/2020/mobileassets/001-26051/B1CF7C35-D704-4F2D-82D1-DCE47CD14C5C/com_apple_MobileAsset_Font6/ce51ca1d8fea058f7c61047c2b2bb90b08060280.zip
Maku , Regular , Maku , Regular , INDIC , 1.97 MB , http://updates-http.cdn-apple.com/2020/mobileassets/001-26051/B1CF7C35-D704-4F2D-82D1-DCE47CD14C5C/com_apple_MobileAsset_Font6/c1d66362d7dec365afaa52921f7feb9c874e8a4a.zip

运行convert_font.py需安装 opencc afdko
pip3 install opencc afdko

site-packages/afdko/otc2otf.py

for ft_idx in range(num_fonts):
   font = TTFont(ttc_path, fontNumber=ft_idx, lazy=True)
改为font = TTFont(ttc_path, fontNumber=ft_idx, lazy=True, recalcTimestamp=False) #分解ttc之类字体集时不会写入修改时间
   spot -thead myfont.otf 查看 modified 时间

            save_path = os.path.join(os.path.dirname(ttc_path), font_filename)
            font.save(save_path)
加入条件解包字体集略过.开头命名字体 windows不适用
            if not font_filename.startswith("."):
                font.save(save_path)

