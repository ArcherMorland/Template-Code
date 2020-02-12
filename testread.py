import os, random, shutil

import glob

from PIL import Image

import torch
import torch.utils.data as data

import torch
import torch.utils.data as data
import torchvision
import torchvision.transforms.functional as TF
from torchvision import transforms, datasets

import matplotlib.pyplot as plt


def show(imgT):
    plt.imshow(imgT.permute(1,2,0))#PyTorch Tensors ("Image tensors") are channel first, so to use them with matplotlib user need to reshape it
                                   #https://stackoverflow.com/questions/53623472/how-do-i-display-a-single-image-in-pytorch/53633017
                                   #像素顺序是RGB(critical reference!!!!): https://www.jianshu.com/p/c0ba27e392ff
                                   #to gray_scale:https://stackoverflow.com/questions/52439364/how-to-convert-rgb-images-to-grayscale-in-pytorch-dataloader
    plt.show()


Train_root=os.path.join('..','train','bedroom')

ImgH=416 
ImgW=416

transform = transforms.Compose([transforms.Resize(size=(ImgH, ImgW), interpolation=2)]) 
imgPath=glob.glob(os.path.join(Train_root,'*.*'))


trimgs=None
for i, ip in enumerate(imgPath):
    
    image=TF.to_tensor(transform(Image.open(ip).convert('RGB')))
    if i == 0:
        trimgs=image.view(-1, 3, ImgH, ImgW)

    else:
        trimgs=torch.cat([trimgs, image.view(-1, 3, ImgH, ImgW)], 0)

    '''
    show(image)
    if i>1:
        break'''


print(trimgs.shape)







