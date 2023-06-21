import os
import torch
import torch.nn as nn
from nowcasting.models import nowcastnet

class Model(object):
    def __init__(self, configs):
        self.configs = configs
        networks_map = {
            'NowcastNet': nowcastnet.Net,
        }
        self.data_frame = []
        
        if configs.model_name in networks_map:
            Network = networks_map[configs.model_name]
            self.network = Network(configs).to(configs.device)
            self.test_load()

        else:
            raise ValueError('Name of network unknown %s' % configs.model_name)

    def test_load(self):
        stats = torch.load(self.configs.pretrained_model)
        self.network.load_state_dict(stats)

    def test(self, frames):
        frames_tensor = torch.FloatTensor(frames).to(self.configs.device)
        self.network.eval()
        with torch.no_grad():
            next_frames = self.network(frames_tensor)
        return next_frames.detach().cpu().numpy()