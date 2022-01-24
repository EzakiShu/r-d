# Copyright Niantic 2019. Patent Pending. All rights reserved.
#
# This software is licensed under the terms of the Monodepth2 licence
# which allows for non-commercial use only, the full terms of which are made
# available in the LICENSE file.

from __future__ import absolute_import, division, print_function

import os
import sys
import glob
import argparse
import numpy as np
import PIL.Image as pil
import matplotlib as mpl
import matplotlib.cm as cm

import torch
from torchvision import transforms, datasets

import networks
from layers import disp_to_depth
from utils import download_model_if_doesnt_exist
from evaluate_depth import STEREO_SCALE_FACTOR

import time

device  = None
feed    = {}
encoder = None
depth_decoder = None

def parse_args():
    parser = argparse.ArgumentParser(
        description='Simple testing funtion for Monodepthv2 models.')

    parser.add_argument('--image_path', type=str,
                        help='path to a test image or folder of images', required=True)
    parser.add_argument('--model_name', type=str,
                        help='name of a pretrained model to use',
                        choices=[
                            "mono_640x192",
                            "stereo_640x192",
                            "mono+stereo_640x192",
                            "mono_no_pt_640x192",
                            "stereo_no_pt_640x192",
                            "mono+stereo_no_pt_640x192",
                            "mono_1024x320",
                            "stereo_1024x320",
                            "mono+stereo_1024x320"])
    parser.add_argument('--ext', type=str,
                        help='image extension to search for in folder', default="jpg")
    parser.add_argument("--no_cuda",
                        help='if set, disables CUDA',
                        action='store_true')
    parser.add_argument("--pred_metric_depth",
                        help='if set, predicts metric depth instead of disparity. (This only '
                             'makes sense for stereo-trained KITTI models).',
                        action='store_true')

    return parser.parse_args()


def load_model(args):
    """Function to predict for a single image or folder of images
    """
    assert args.model_name is not None, \
        "You must specify the --model_name parameter; see README.md for an example"

    if torch.cuda.is_available() and not args.no_cuda:
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    if args.pred_metric_depth and "stereo" not in args.model_name:
        print("Warning: The --pred_metric_depth flag only makes sense for stereo-trained KITTI "
              "models. For mono-trained models, output depths will not in metric space.")

    download_model_if_doesnt_exist(args.model_name)
    model_path = os.path.join("models", args.model_name)
    print("-> Loading model from ", model_path)
    encoder_path = os.path.join(model_path, "encoder.pth")
    depth_decoder_path = os.path.join(model_path, "depth.pth")

    # LOADING PRETRAINED MODEL
    start_load = time.perf_counter() 
    print("   Loading pretrained encoder")
    encoder = networks.ResnetEncoder(18, False)
    loaded_dict_enc = torch.load(encoder_path, map_location=device)

    # extract the height and width of image that this model was trained with
    feed_height = loaded_dict_enc['height']
    feed_width = loaded_dict_enc['width']
    filtered_dict_enc = {k: v for k, v in loaded_dict_enc.items() if k in encoder.state_dict()}
    encoder.load_state_dict(filtered_dict_enc)
    encoder.to(device)
    encoder.eval()

    print("   Loading pretrained decoder")
    depth_decoder = networks.DepthDecoder(
        num_ch_enc=encoder.num_ch_enc, scales=range(4))

    loaded_dict = torch.load(depth_decoder_path, map_location=device)
    depth_decoder.load_state_dict(loaded_dict)

    depth_decoder.to(device)
    depth_decoder.eval()

    print(" Fin_load: {} s".format(time.perf_counter() - start_load))

    feed = {
      "height": feed_height,
      "width" : feed_width
    } 
    return device, feed, encoder, depth_decoder


def load_image(args):
    # FINDING INPUT IMAGES
    if os.path.isfile(args.image_path):
        # Only testing on a single image
        paths = [args.image_path]
        output_directory = os.path.dirname(args.image_path)
    elif os.path.isdir(args.image_path):
        # Searching folder for images
        paths = glob.glob(os.path.join(args.image_path, '*.{}'.format(args.ext)))
        output_directory = args.image_path
    else:
        raise Exception("Can not find args.image_path: {}".format(args.image_path))

    print("-> Predicting on {:d} test images".format(len(paths)))

    return image

def est_image(input_image, device, feed, encoder, depth_decoder):
    with torch.no_grad():
      start_estimate = time.perf_counter() 
      # Load image and preprocess
      start_prep = time.perf_counter()
      # input_image = pil.open(image_path).convert('RGB')
      original_width, original_height = input_image.size
      input_image = input_image.resize((feed["width"], feed["height"]), pil.LANCZOS)
      input_image = transforms.ToTensor()(input_image).unsqueeze(0)
      print(" -- Fin_prep: {} s".format(time.perf_counter() - start_prep))

      # PREDICTION
      start_predict = time.perf_counter()
      input_image = input_image.to(device)
      features = encoder(input_image)
      outputs = depth_decoder(features)
      print(" -- Fin_predict: {} s".format(time.perf_counter() - start_predict))

      disp = outputs[("disp", 0)]
      disp_resized = torch.nn.functional.interpolate(
          disp, (original_height, original_width), mode="bilinear", align_corners=False)

      # Saving colormapped depth image
      disp_resized_np = disp_resized.squeeze().cpu().numpy()
      vmax = np.percentile(disp_resized_np, 95)
      normalizer = mpl.colors.Normalize(vmin=disp_resized_np.min(), vmax=vmax)
      mapper = cm.ScalarMappable(norm=normalizer, cmap='magma')
      colormapped_im = (mapper.to_rgba(disp_resized_np)[:, :, :3] * 255).astype(np.uint8)
      im = pil.fromarray(colormapped_im)

      print('-> Done!')
      print(" Fin_estimate: {} s".format(time.perf_counter() - start_estimate))

    return im


if __name__ == '__main__':
    # args = parse_args()
    # print(args)
    art_args = type("hoge", (object,), {
      "ext"               : "jpg",
      "image_path"        : "input/0000000006.png",
      "model_name"        : "mono_1024x320",
      "no_cuda"           : False,
      "pred_metric_depth" : False
    })
    
    print(art_args)
    # test_simple(art_args)

    image = pil.open(art_args.image_path).convert('RGB')
    device, feed, encoder, depth_decoder = load_model(art_args)
    res_image = est_image(image, device, feed, encoder, depth_decoder)
