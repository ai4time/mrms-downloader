import numpy as np
import os, shutil
import pickle
import random
import torch
from torch.utils.data import Dataset, DataLoader
from datetime import datetime, timedelta
import cv2

class InputHandle(Dataset):
    def __init__(self, input_param):
        self.input_data_type = input_param.get('input_data_type', 'float32')
        self.output_data_type = input_param.get('output_data_type', 'float32')
        self.img_width = input_param['image_width']
        self.img_height = input_param['image_height']
        self.length = input_param['total_length']
        self.input_length = input_param['input_length']
        self.data_path = input_param['data_path']
        self.type = input_param['type'] #train/test/valid
        self.present_time = datetime.strptime(input_param['present_time'],
                                            "%Y%m%d-%H%M%S"  )

        self.case_list = []
        self.case_list = self.generate_observations()
        self.case_list = [self.case_list]

    def generate_observations(self):
        temp_time = self.present_time
        ten_min_delta = timedelta(minutes=10)
        case_list = []
        for i in range(self.input_length):
            temp_path = self.datetime2path(temp_time)
            case_list.append(temp_path)
            temp_time = temp_time - ten_min_delta
        return case_list

    def datetime2path(self, temptime):
        path = temptime.strftime("%Y/%m/%d/mrms/ncep/PrecipRate/PrecipRate_00.00_%Y%m%d-%H%M%S.uint16.png")
        path = self.data_path + '/' + path
        return path

    def load(self, index):
        data = []
        for img_path in self.case_list[index]:
            img = cv2.imread(img_path, 2)
            shape = img.shape
            img = cv2.resize(img, (shape[1]//2, shape[0]//2))
            data.append(np.expand_dims(img, axis=0))
        print('data_type:', np.concatenate(data, axis=0).dtype,
              'data_shape:', np.concatenate(data, axis=0).shape,
              'max:', np.max(np.concatenate(data, axis=0)), 
              'min:', np.min(np.concatenate(data, axis=0)), )
        data = np.concatenate(data, axis=0).astype(self.input_data_type) / 10.0 - 3.0
        # print('data shape: ', data.shape) 
        data = np.pad(data, ((0, 0), (21, 21), (42, 42)), mode='constant', constant_values=0)

        assert data.shape[1]==1792 and data.shape[2]==3584
        return data

    def __getitem__(self, index):
        data = self.load(index)[-self.length:].copy()
        print('processed_data', np.max(data), np.min(data))

        mask = np.ones_like(data)
        mask[data < 0] = 0
        data[data < 0] = 0
        data = np.clip(data, 0, 128)
        vid = np.zeros((self.input_length, self.img_height, self.img_width, 2))
        vid[..., 0] = data
        vid[..., 1] = mask
        img = dict()
        img['radar_frames'] = vid
        return img

    def __len__(self):
        return len(self.case_list)
