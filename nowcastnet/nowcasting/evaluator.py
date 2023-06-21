import os.path
import datetime
import cv2
import numpy as np
import torch
import pickle
from PIL import Image
import matplotlib.pyplot as plt

def test_pytorch_loader(model, test_input_handle, configs, itr):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') , 'test...')
    res_path = os.path.join(configs.gen_frm_dir, str(itr))
    if not os.path.exists(res_path):
        os.mkdir(res_path)

    for batch_id, test_ims in enumerate(test_input_handle):

        test_ims = test_ims['radar_frames'].numpy()
        img_gen = model.test(test_ims)
        output_length = configs.total_length - configs.input_length

        def save_plots(field, labels, res_path, figsize=None,
                       vmin=0, vmax=10, cmap="viridis", mpl=False, npy=False, png=True, **imshow_args):

            for i, data in enumerate(field):
                if mpl:
                    fig = plt.figure(figsize=figsize)
                    ax = plt.axes()
                    ax.set_axis_off()
                    alpha = data[..., 0] / 1
                    alpha[alpha < 0.5] = 0
                    alpha[alpha > 0.5] = 1
                    # alpha = (data > 0).astype(data)
                    img = ax.imshow(data[..., 0], alpha=alpha, 
                                    vmin=vmin, vmax=vmax, cmap=cmap, **imshow_args)
                    plt.savefig('{}/{}.jpg'.format(res_path, labels[i]))
                    plt.close()  
                if npy:
                    with open('{}/{}.npy'.format(res_path, labels[i]), 'wb') as f:
                        np.save(f, data[..., 0])
                if png:
                    img = (data + 3) * 10
                    img = np.clip(img, 0, 65536)
                    img = img.astype(np.uint16)
                    # img = np.expand_dims(img, axis=2)
                    img = Image.fromarray(img, 'I;16')
                    # cv2.imwrite('{}/{}.png'.format(res_path, labels[i]), img)
                    img.save('{}/{}.png'.format(res_path, labels[i]))


        data_vis_dict = {
            'radar': {'vmin': 0, 'vmax': 40},
        }
        vis_info = data_vis_dict[configs.dataset_name]

        if batch_id <= configs.num_save_samples:
            # path = os.path.join(res_path, str(batch_id))
            # os.mkdir(path)
            if configs.case_type == 'normal':
                test_ims_plot = test_ims[0][:-2, 256-192:256+192, 256-192:256+192]
                img_gen_plot = img_gen[0][:-2, 256-192:256+192, 256-192:256+192]
            elif configs.case_type == 'full':
                test_ims_plot = test_ims[0][:-2, 21:-21, 42:-42]
                img_gen_plot = img_gen[0][:-2,  21:-21, 42:-42]
            else:
                test_ims_plot = test_ims[0][:-2]
                img_gen_plot = img_gen[0][:-2]
            print('range:', np.min(test_ims_plot), np.max(test_ims_plot))
            # save_plots(test_ims_plot,
            #            labels=['gt{}'.format(i + 1) for i in range(configs.input_length)],
            #            res_path=path, vmin=vis_info['vmin'], vmax=vis_info['vmax'])
            print('range:', np.min(img_gen_plot), np.max(img_gen_plot))
            path = check_path(root_path=configs.output_path + '/results', time=configs.present_time, 
                              model_name=configs.model_name)
            
            save_plots(img_gen_plot,
                       labels=[f'pd{(i+1)*10}-min' for i in range(configs.total_length - configs.input_length)],
                       res_path=path, vmin=vis_info['vmin'], vmax=vis_info['vmax'], figsize=(20, 10), png=True)

    print('finished!')


def check_path(root_path, time, model_name):
    present_time = datetime.datetime.strptime(time, "%Y%m%d-%H%M%S")
    date = present_time.strftime("%Y%m%d")
    minute = present_time.strftime("%H%M%S")

    model_path = '/'.join([root_path, model_name])
    date_path = '/'.join([root_path, model_name, date])
    minute_path = '/'.join([root_path, model_name, date, minute])

    paths = [root_path, model_path, date_path, minute_path]
    for path in paths:    
        if not os.path.exists(path):
            os.mkdir(path)
    return minute_path
