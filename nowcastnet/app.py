import argparse
import json
import os
import shutil
import time
from datetime import datetime, timedelta

import anylearn
import torch

import nowcasting.evaluator as evaluator
from nowcasting.data_provider import datasets_factory
from nowcasting.models.model_factory import Model


torch.backends.cudnn.enabled = True
torch.backends.cudnn.benchmark = True


if os.environ.get('ANYLEARN_TASK_ID', None) is not None:
    pretrained_model_path = str(anylearn.get_model("chenky/mrms_nowcastnet").download())
    dataset_path = str(anylearn.get_dataset("yhuang/MRMS").download())
    output_path = str(anylearn.get_dataset("yhuang/MRMS-RT").download())
else:
    pretrained_model_path = ""
    dataset_path = "./data"
    output_path = "./data"

# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='NowcastNet')

parser.add_argument('--device', type=str, default='cpu:0')
parser.add_argument('--worker', type=int, default=1)
parser.add_argument('--cpu_worker', type=int, default=1)
parser.add_argument('--dataset_name', type=str, default='radar')
parser.add_argument('--input_length', type=int, default=9)
parser.add_argument('--total_length', type=int, default=29)
parser.add_argument('--img_height', type=int, default=512)
parser.add_argument('--img_width', type=int, default=512)
parser.add_argument('--img_ch', type=int, default=2)
parser.add_argument('--case_type', type=str, default='normal')
parser.add_argument('--model_name', type=str, default='nowcasting')
parser.add_argument('--gen_frm_dir', type=str, default='results/nowcasting')
parser.add_argument('--pretrained_model', type=str, default=pretrained_model_path)
parser.add_argument('--batch_size', type=int, default=1)
parser.add_argument('--num_save_samples', type=int, default=10)
parser.add_argument('--ngf', type=int, default=32)
parser.add_argument('--dataset_path', type=str, default=dataset_path)
parser.add_argument('--output_path', type=str, default=dataset_path)

parser.add_argument('--present_time', type=str)

args = parser.parse_args()

args.evo_ic = args.total_length - args.input_length
args.gen_oc = args.total_length - args.input_length
args.ic_feature = args.ngf * 10

def test_wrapper_pytorch_loader(model, configs):
    batch_size_test = configs.batch_size
    test_input_handle = datasets_factory.data_provider(args)
    args.batch_size = batch_size_test
    evaluator.test_pytorch_loader(model, test_input_handle, configs, 'test_result')

if os.path.exists(args.gen_frm_dir):
    shutil.rmtree(args.gen_frm_dir)
os.makedirs(args.gen_frm_dir)

print('Initializing models')

model = Model(args)


def next_time(present_time, delta_min = 2):
    timedelta_2min = timedelta(minutes=delta_min)
    present_time = datetime.strptime(present_time, "%Y%m%d-%H%M%S")
    present_time = present_time + timedelta_2min
    present_time = present_time.strftime("%Y%m%d-%H%M%S")
    return present_time


def check_path(present_time):
    present_time = datetime.strptime(present_time, "%Y%m%d-%H%M%S")
    for i in range(args.input_length):
        path = present_time.strftime("%Y/%m/%d/mrms/ncep/PrecipRate/PrecipRate_00.00_%Y%m%d-%H%M%S.uint16.png")
        path = args.dataset_path + '/' + path
        if not os.path.exists(path):
            return False
        present_time = present_time - timedelta(minutes=10)
    return True

def nowcastnet():
    counter = 0
    missing_log = {"missing": []}
    while True:
        # update config time
        if check_path(args.present_time):
            # run the model and save outputs
            test_wrapper_pytorch_loader(model, args)
            args.present_time = next_time(args.present_time) 

            # repair the counter
            counter = 0
        else:
            time.sleep(5)
            counter += 1
        
            missing_log["missing"].append(args.present_time)
            with open('results/missing_log.json', 'w') as f:
                json.dump(missing_log, f)
            if check_path(next_time(args.present_time)):
                args.present_time = next_time(args.present_time) 


if __name__ == '__main__':
    nowcastnet()
