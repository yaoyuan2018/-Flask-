import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os

#天空区域提取函数
def skyRegion1(picname):
    iLow = np.array([90,43,46])
    iHigh = np.array([140,255,255])

    picname = 'app/static/tmp/' + picname
    img = cv2.imread(picname)              #cv2.imread()读入图像，第二个参数告诉函数应该如何读取这幅图片。
    imgOriginal = cv2.imread(picname)      #cv2.IMREAD_COLOR:读入一幅彩色图像。图像的透明度会被忽略。
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)    #cv.IMREAD_GRAYSCALE:以灰度模式读入图像
                                                  #cv2.cvtColor(image, cv2.COLOR_BGR2HSV)把图像从RBG转到HSV颜色空间，注意是BGR2HSV不是RGB2HSV，因为OpenCV默认的颜色空间是BGR，类似于RGB，但不是RGB。
    #hsv split
    h,s,v = cv2.split(img)           #通道分离
    v = cv2.equalizeHist(v)          #对直方图进行均衡化
    hsv = cv2.merge((h,s,v))

    imgThresholded = cv2.inRange(hsv, iLow, iHigh)  #.inRange函数设置阈值，去除背景部分；iLow指图像中低于iLow的值，图像值变为0；iHigh指图像中高于iHigh的值，图像值变为0；而在iLow和iHigh之间的值变成255
                                                    #此处分出我们需要的蓝色阈值区域。
    imgThresholded = cv2.medianBlur(imgThresholded,9)  #调用中值滤波器消除噪点，imgThresholded是待处理图像，9是孔径尺寸

    #open
    kernel = np.ones((5,5),np.uint8)               #赋值一个5X5矩阵，且矩阵元素皆为1
    imgThresholded = cv2.morphologyEx(imgThresholded,cv2.MORPH_OPEN,kernel,iterations = 10)
    #腐蚀后的图像
    imgThresholded = cv2.medianBlur(imgThresholded, 9) #调用中值滤波器消除噪点

    #保存图片
    pic_name = picname.split('/')[-1].split('.')[0]

    tmp = "app/static/tmp/"+pic_name+"-mask.jpg"

    cv2.imwrite(tmp, imgThresholded)     #cv2.imwrite(file, img, num) file:要保存的文件名 img：要保存的图像 num:可选参数，图像质量
    return tmp                           #生成的图像保存在tmp文件夹中


def seamClone(skyname, picname, maskname):
    # Read images
    sky_name = skyname.split('/')[-1].split('.')[0]
    pic_name = picname.split('/')[-1].split('.')[0]
    skyname1 = 'app/static/tmp/' + skyname
    picname1 = 'app/static/tmp/' + picname

    src = cv2.imread(skyname1)
    dst = cv2.imread(picname1)
    mask = cv2.imread(maskname,0)
    module_path = os.path.dirname(__file__)

    _,contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  #cv2.findContours()函数查找检测物体的轮廓
    #mask图像对象；cv2.RETR_TREE：建立一个等级树结构的轮廓；cv2.CHAIN_APPROX_SIMPLE：轮廓narray中只存储可以用直线描述轮廓的点的个数
    line = []
    list = []
    for i in range(len(contours)):
        for j in range(len(contours[i])):
            line.append(contours[i][j][0][0])
            list.append(contours[i][j][0][1])

    maxline = np.max(line)
    minline = np.min(line)
    maxlist = np.max(list)
    minlist = np.min(list)

    for i in range(len(contours)):
        if len(contours[i]) >= 4:
            cnt = contours[i][0:4]
            break
    cnt[0][0][0] = minline
    cnt[0][0][1] = maxlist
    cnt[1][0][0] = maxline
    cnt[1][0][1] = maxlist
    cnt[2][0][0] = maxline
    cnt[2][0][1] = minlist
    cnt[3][0][1] = minline

    x, y, w, h = cv2.boundingRect(cnt)

    src = cv2.resize(src, (w, h), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite("src_sky.jpg", src)

    center = (int((maxline+minline)/2), int((maxlist+minlist)/2))

    output = cv2.seamlessClone(src, dst, mask, center, cv2.NORMAL_CLONE)

    tmp1 = "app/static/tmp/" + pic_name + "-" + sky_name + ".jpg"
    tmp = "../static/tmp/"+pic_name+"-"+sky_name+".jpg"

    cv2.imwrite(tmp1,output)

    return tmp

def myfilter(picname, filtername):
    pic_name = picname.split('/')[-1].split('.')[0].split('-')[0]
    picname = "app/static/tmp/"+pic_name+".jpg"
    # print(picname)
    img = np.array(cv2.imread(picname))
    # 以数组形式打开要添加滤镜的图片
    img2 = np.array(cv2.imread(filtername))
    # 以数组形式打开滤镜颜色映射参照表


    style_name = filtername.split('/')[-1].split('.')[0]

    tmp = "app/static/tmp/"+pic_name+"-"+style_name+".jpg"
    tmp1 = "../static/tmp/"+pic_name+"-"+style_name+".jpg"
    x = []  #数组x用于保存图像所有像素的R值
    y = []  #数组Y用于保存图像所有像素的G值
    z = []  #数组Z用于保存图像所有相熟的B值

    for i in range(len(img)):
        x.extend(img[i][:, 0])
        y.extend(img[i][:, 1])
        z.extend(img[i][:, 2])
    #遍历三个数组
    y = np.array(y)
    x = np.array(x)
    z = np.array(z)
    pos_x = np.floor(y / 4).astype(np.int32) + np.floor(x / 32).astype(np.int32) * 64
    pos_y = np.floor(z / 4).astype(np.int32) + np.floor((x % 32) / 16).astype(np.int32) * 64
    #矩阵运算，对所有像素点的RGB值，计算该像素在颜色映射对照表上的位置，以上为X轴和Y轴位置公式
    count = 0
    for i in range(len(img)):
        for j in range(len(img[i])):
            img[i][j] = img2[pos_x[count]][pos_y[count]]
            count += 1
    #遍历坐标矩阵中的值，进行逐点颜色映射
    cv2.imwrite(tmp, img)

    return tmp1

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
    module_path = os.path.dirname(__file__)
    font = module_path+'/../static/arial unicode ms.ttf'
    #设定字体样式
    fileurl = module_path+'/../static/tmp/' + in_file
    img = Image.open(fileurl).convert('RGB')
    #以RGB形式读取图片
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
    tmp1 = module_path+'/../static/tmp/watermark-' + str(opacity) + '-' + text + '-' + in_file
    tmp = "../static/tmp/watermark-" + str(opacity) + '-' + text + '-' + in_file
    output = Image.composite(watermark, img, watermark)
    output.save(tmp1)

    return tmp

def cartoon_add(picname):
    pic_name = picname.split('/')[-1].split('.')[0].split('-')[0]
    picname = "app/static/tmp/" + pic_name + ".jpg"
    num_down = 2  # 缩减像素采样的数目
    num_bilateral = 9  # 定义双边滤波的数目
    img_rgb = cv2.imread(picname)
    # 用高斯金字塔降低取样
    img_color = img_rgb
    for _ in range(num_down):
        img_color = cv2.pyrDown(img_color)
    print(img_color.shape)
    # 重复使用小的双边滤波代替一个大的滤波
    for _ in range(num_bilateral):
        img_color = cv2.bilateralFilter(img_color, d=7,  # d是领域的直径，sigmaColor是空间高斯函数标准差，sigmaSpace是灰度值相似性高斯函数标准差
                                        sigmaColor=9,
                                        sigmaSpace=7)
    # 升采样图片到原始大小
    for _ in range(num_down):
        img_color = cv2.pyrUp(img_color)

    if img_color.shape is not img_rgb.shape:
        height, width = img_rgb.shape[:2]
        size = (width, height)
        print(size)
        img_color = cv2.resize(img_color, size, interpolation=cv2.INTER_AREA)

    # 转图片为灰度，并使用中值滤波器减少噪点
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)

    # 创建轮廓
    img_edge = cv2.adaptiveThreshold(img_blur, 255,
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY,
                                     blockSize=9,
                                     C=2)

    # 合并轮廓与彩色图片
    # 转换回彩色图像

    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)

    img_cartoon = cv2.bitwise_and(img_color, img_edge)

    # 显示图片
    tmp = "app/static/tmp/" + pic_name + "-cartoon.jpg"
    tmp1 = "../static/tmp/" + pic_name + "-cartoon.jpg"

    cv2.imwrite(tmp, img_cartoon)
    return tmp1