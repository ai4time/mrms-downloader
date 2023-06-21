

# NowcastNet

This repository is the source code for the NowcastNet model proposed in paper 'Skillful nowcasting of extreme precipitation with NowcastNet'.

## Environment
Run the code directly on Code Ocean, or install the environment following these steps:
1. Find a device with GPU support. Our experiment is conducted on a single RTX GPU with more than 24 GB and in the Linux system.
2. Install Python >= 3.6 and install the environment with the following script.

```bash
pip install -r requirements.txt
```

## Experiment

Please click the 'Reproducible Run' botton to run the experiments on the US events shown in the article. 

In the 'results/us/test_result' directory, folder '0' to folder '9' correspond to Fig. 2 in the main text, Extended Data Fig. 2-6 and Supplementary Fig.2-5 in order. 

In the 'results/us_large/test_result' directory, folder '0' corresponds to Extended Data Fig. 9. 

Or execute the code with following scripts.

```bash
bash ./mrms_case_test.sh # Experiments on events shown in Fig. 2, Extended Data Fig. 2-6 and Supplementary Fig.2-5.
bash ./mrms_large_case_test.sh # Experiments on events shown in Extended Data Fig. 9.
```

For the results on the evaluation dataset, please download the dataset from [[Tsinghua Cloud]](https://cloud.tsinghua.edu.cn/d/b9fb38e5ee7a4dabb2a6/). And place all the events (00000-95999) under the `/data/dataset/mrms/figure/` folder. Then run the model with the following script.

```bash
bash ./mrms_case_test.sh
```


