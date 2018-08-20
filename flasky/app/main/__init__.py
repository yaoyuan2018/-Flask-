from flask import Blueprint
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import numpy as np

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission

@main.app_context_processor        #把Permission类加入模板上下文
def inject_permissions():
    return dict(Permission=Permission)

def add_watermark(in_file, text, opacity):
    '''
    :param in_file: 要添加水印的图片
    :param text:  文字水印内容
    :param out_file: 添加水印后的图片
    :param font:水印字体
    :param angle: 水印旋转角度
    :param opacity: 水印透明度
    '''

    angle=23

    font = "../static/arial unicode ms.ttf"
    img = Image.open(in_file).convert('RGB')
    watermark = Image.new('RGBA',img.size,(0,0,0,0))
    size = 2
    n_font = ImageFont.truetype(font,size)
    #getsize返回水印文字对应字体大小的宽度和高度
    n_width,n_height = n_font.getsize(text)
    #找到使得水印文字宽度最接近对应字体大小的宽度和高度

    while n_width + n_height< watermark.size[0]:
        size += 2
        n_font = ImageFont.truetype(font,size)
        n_width,n_height = n_font.getsize(text)
    draw = ImageDraw.Draw(watermark,'RGBA')
    draw.text(((watermark.size[0] - n_width)/2,(watermark.size[1]-n_height)/2),text, font=n_font)
    watermark = watermark.rotate(angle,Image.BICUBIC)
    alpha = watermark.split()[3]
    #通过降低亮度和对比对来降低水印的透明度
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    # 设置透明度
    watermark.putalpha(alpha)
    # 添加水印
    tmp = "../static/tmp/" + in_file + "-watermark.jpg"
    output = Image.composite(watermark, img, watermark)
    cv2.imwrite(tmp,output)

    return tmp