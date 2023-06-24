import argparse
import os
import shutil

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

def test_wrapper_pytorch_loader(model):
    batch_size_test = args.batch_size
    test_input_handle = datasets_factory.data_provider(args)
    args.batch_size = batch_size_test
    evaluator.test_pytorch_loader(model, test_input_handle, args, 'test_result')

if os.path.exists(args.gen_frm_dir):
    shutil.rmtree(args.gen_frm_dir)
os.makedirs(args.gen_frm_dir)

print('Initializing models')

model = Model(args)

test_wrapper_pytorch_loader(model)
