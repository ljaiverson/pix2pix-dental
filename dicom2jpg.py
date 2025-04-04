# -*- coding: utf-8 -*-
# @Author: Jun Luo
# @Date:   2021-01-09 18:04:24
# @Last Modified by:   Jun Luo
# @Last Modified time: 2022-06-13 14:23:47

import pydicom
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import numpy as np

import os
# import cv2
import shutil
import glob
import copy

import tqdm

def dcm2jpg(source_fn1, output_fn1, source_fn2, output_fn2, img_h=334, img_w=334):
    ds1 = pydicom.dcmread(source_fn1)
    ds_array1 = ds1.pixel_array
    if ds_array1.max() == 0:
        return 1
    ds2 = pydicom.dcmread(source_fn2)
    ds_array2 = ds2.pixel_array
    if ds_array2.max() == 0:
        return 1
    for ds_array, output_fn in zip([ds_array1, ds_array2], [output_fn1, output_fn2]):
        img_array = (ds_array / ds_array.max() * 255).astype(int) 
        img = Image.fromarray(img_array).convert("L").resize((img_h, img_w))
        # plt.imshow(img)
        # plt.show()
        img.save(output_fn)
    return 0

if __name__ == '__main__':
    # define input and output folders
    dcm_parent_folder = "./metadata/dataset_2022/"
    prefix = ["1-07", "10-03", "81-3", "86-1"]
    black_cnt = 0
    total_uld_src_fns = []
    total_norm_src_fns = []
    total_uld_dst_fns = []
    total_norm_dst_fns = []
    for i in tqdm.tqdm(range(4)):
        uld_src_folder = os.path.join(dcm_parent_folder, f"{prefix[i]} ULD/")
        norm_src_folder = os.path.join(dcm_parent_folder, f"{prefix[i]} NORM/")
        uld_output_folder = f"./datasets/data{i+1}/train_A/"
        norm_output_folder = f"./datasets/data{i+1}/train_B/"
        for fo in [uld_output_folder, norm_output_folder]:
            if os.path.exists(fo):
                shutil.rmtree(fo)
            os.makedirs(fo)

        # get source fns
        uld_src_fns = []
        norm_src_fns = []
        for fn in glob.glob(uld_src_folder + "*.dcm"):
            tail_fn = os.path.split(fn)[1]
            norm_fn = norm_src_folder + tail_fn.replace("ULD", "NORM")
            if os.path.exists(norm_fn):
                norm_src_fns.append(norm_fn)
                uld_src_fns.append(fn)
        # print(f"Norm has {len(norm_src_fns)} pics, and ULD has {len(uld_src_fns)} pics")

        # check format and collect tail fns
        norm_tail_fns = []
        uld_tail_fns = []
        for uld_fn in uld_src_fns:
            uld_tail = os.path.split(uld_fn)[1]
            uld_tail_fns.append(uld_tail)
        for norm_fn in norm_src_fns:
            norm_tail = os.path.split(norm_fn)[1]
            norm_tail_fns.append(norm_tail)

        # create output fns
        norm_dst_fns = []
        uld_dst_fns = []
        for norm_tail in norm_tail_fns:
            norm_tail = norm_tail.replace(" NORM", "")
            norm_tail = norm_tail.replace(".dcm", ".jpg")
            norm_dst_fns.append(norm_output_folder + norm_tail)
        for uld_tail in uld_tail_fns:
            uld_tail = uld_tail.replace(" ULD", "")
            uld_tail = uld_tail.replace(".dcm", ".jpg")
            uld_dst_fns.append(uld_output_folder + uld_tail)

        # # check output length and matchness
        # print(f"Norm has {len(norm_dst_fns)} pics, and ULD has {len(uld_dst_fns)} pics")
        # for fn1, fn2 in zip(norm_dst_fns, uld_dst_fns):
        #     if os.path.split(fn1)[1] != os.path.split(fn2)[1]:
        #         print("### The following does not match", fn1, fn2)

        total_uld_src_fns += copy.deepcopy(uld_src_fns)
        total_norm_src_fns += copy.deepcopy(norm_src_fns)
        total_uld_dst_fns += copy.deepcopy(uld_dst_fns)
        total_norm_dst_fns += copy.deepcopy(norm_dst_fns)
    
    # dcm2jpg
    print("==> copying pics...")
    for uld_src_fn, uld_dst_fn, norm_src_fn, norm_dst_fn in tqdm.tqdm(zip(total_uld_src_fns, total_uld_dst_fns, total_norm_src_fns, total_norm_dst_fns)):
        black_cnt += dcm2jpg(uld_src_fn, uld_dst_fn, norm_src_fn, norm_dst_fn)
    print(f"[{black_cnt}/{len(total_uld_src_fns)}] images are black, these pairs are ignored")



