#! python3
import os
import subprocess
from PIL import Image
import logging as log

import debug_config

from load_settings import load_settings
from image_list import image_list

def make_image_thumbnail(image_lists: dict, dirs_list: dict):
    log.debug('-> make_image_thumbnail()')

    # jpg, png をサムネイル処理する
    candidate_img_list = image_lists['candidate_img_list']

    for i in range(len(candidate_img_list)):
        # 候補リストに基づいて jpg, png を読む
        image_obj = Image.open(dirs_list['src_img_dir'] + candidate_img_list[i])
        image_obj = image_obj.convert('RGB') # 必要???

        # アスペクト比によって別処理
        pixel_width = image_obj.width
        pixel_height = image_obj.height
        
        if pixel_width > pixel_height:
            # 横長ならそのままリサイズ
            image_obj.thumbnail((480, 360), Image.LANCZOS)
        else:
            # 縦長なら正方形にクリッピングしてリサイズ
            image_obj = image_obj.crop((0, (pixel_height - pixel_width)/2, pixel_width, pixel_width + (pixel_height - pixel_width)/2))
            image_obj.thumbnail((360, 360), Image.LANCZOS)
    
        # 一旦pngとして出力
        tmp_name = candidate_img_list[i].split('.')[0]
        tmp_path = dirs_list['tmb_img_dir'] + 'tmb_' + tmp_name + '.png'
        image_obj.save(tmp_path)
        #image_obj.save(dirs_list['tmb_img_dir'] + 'tmb_' + tmp_name + '.jpg', quality=95) # jpgの場合

        log.debug('saved_tmp-tmb: ' + 'tmb_' + tmp_name + '.png')
        
        # mozjpg を呼び出してjpgに圧縮する
        log.debug('| -> run MozJPEG')
        
        output_path = dirs_list['tmb_img_dir'] + 'tmb_' + tmp_name + '.jpg'

        # 圧縮、中間ファイルとして出力
        cp = subprocess.run(['cjpeg-static', '-quality', '90', '-outfile', dirs_list['tmb_img_dir'] + 'intermediate_img.jpg', tmp_path], encoding='utf-8', stdout=subprocess.PIPE)
        log.debug(cp)

        # Exif 等メタデータを削除、最終ファイル出力
        cp = subprocess.run(['jpegtran-static', '-copy', 'none', '-optimize', '-outfile', output_path, dirs_list['tmb_img_dir'] + 'intermediate_img.jpg'], encoding='utf-8', stdout=subprocess.PIPE)
        log.debug(cp)

        log.debug('saved_tmb: ' + 'tmb_' + tmp_name + '.jpg')

        # 中間ファイル削除
        os.remove(tmp_path)
        os.remove(dirs_list['tmb_img_dir'] + 'intermediate_img.jpg')


def make_gif_thumbnail(image_lists: dict, dirs_list: dict):
    log.debug('-> make_gif_thumbnail()')

    # gif をサムネイル処理する
    candidate_gif_list = image_lists['candidate_gif_list']

    for i in range(len(candidate_gif_list)):
        # Gifsicle を呼び出して圧縮する（PIL でやるのは諦めた。）
        log.debug('| -> run Gifsicle')
        
        output_path = dirs_list['tmb_img_dir'] + 'tmb_' + candidate_gif_list[i]
        log.debug(dirs_list['src_img_dir'] + candidate_gif_list[i])

        image_obj = Image.open(dirs_list['src_img_dir'] + candidate_gif_list[i])
        
        # アスペクト比を維持
        size_x = image_obj.width
        size_y = image_obj.height
        resize_height = 240 * size_y // size_x

        # 圧縮、中間ファイルとして出力
        cp = subprocess.run(['gifsicle','--resize', '240x' + str(resize_height), '--optimize=3', '--colors', '256', '--lossy=40', dirs_list['src_img_dir'] + candidate_gif_list[i], '>', output_path], shell=True, encoding='utf-8', stdout=subprocess.PIPE) # shell=True 重要!
        log.debug(cp)

# -------------------------------------------------

if __name__ == '__main__':
    dirs_list = load_settings()
    image_lists = image_list(dirs_list)
    make_image_thumbnail(image_lists, dirs_list)
    make_gif_thumbnail(image_lists, dirs_list)
    #os.system('PAUSE')