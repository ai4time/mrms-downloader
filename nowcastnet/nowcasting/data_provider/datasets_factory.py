from nowcasting.data_provider import loader
from torch.utils.data import Dataset, DataLoader
import numpy as np

datasets_map = {
    'radar': loader,
}

def data_provider(configs):
 
    if configs.dataset_name == 'radar':
        test_input_param = {
                            'image_width': configs.img_width,
                            'image_height': configs.img_height,
                            'input_data_type': 'float32',
                            'is_output_sequence': True,
                            'name': configs.dataset_name + 'test iterator',
                            'total_length': configs.total_length,
                            'input_length': configs.input_length,
                            'data_path': configs.dataset_path,
                            'type': 'test',
                            'present_time': configs.present_time,
                            }
        test_input_handle = datasets_map[configs.dataset_name].InputHandle(test_input_param)
        test_input_handle = DataLoader(test_input_handle,
                                       batch_size=configs.batch_size,
                                       shuffle=False,
                                       num_workers=configs.cpu_worker,
                                       drop_last=True)


    elif configs.dataset_name not in datasets_map:
        raise ValueError('Name of dataset unknown %s' % configs.dataset_name)

    return test_input_handle

