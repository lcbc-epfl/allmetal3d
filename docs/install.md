# Install



You can install AllMetal3D/Water3D using pip. 

First install the correct version of python (e.g in a conda environment)


```
conda create -n allmetal3d python=3.10
```
Then install the pytorch distribution matching your GPU drivers. 

You will need PyTorch 1.12. Install instructions are available here: [PyTorch documentation](https://pytorch.org/get-started/previous-versions/#v1121)

You can find out your Cuda version using `nvidia-smi` in the terminal and checking the top-right corner of the output. 

```
# ROCM 5.1.1 (Linux only)
pip install torch==1.12.1+rocm5.1.1 torchvision==0.13.1+rocm5.1.1 torchaudio==0.12.1 --extra-index-url  https://download.pytorch.org/whl/rocm5.1.1
# CUDA 11.6
pip install torch==1.12.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116
# CUDA 11.3
pip install torch==1.12.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113
# CUDA 10.2
pip install torch==1.12.1+cu102  --extra-index-url https://download.pytorch.org/whl/cu102
```

Finally, install AllMetal3D:

```
pip install allmetal3d
```