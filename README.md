# AllMetal3D


![Inference app](inference_app.png)


AllMetal3D is an improvement of the Metal3D model trained using a wider amount of ions (NA, K, MG, CA, ZN, FE, FE2, CU, CO, MN). 
The model will predict location, identity and geometry for each site. 

Location is very accurate and can be evaluated using the predicted probability. 
Identity also works well with the ion being classed into majority labels (Alkali, MG, CA, ZN, Non zinc transition metal and NoMetal). NoMetal are likely false positive location predictions. 
Geometry prediction works well to differentiate between octahedral and tetrahedral but not so well for the other classes. 


## How to run

In webbrowser for single structures and visual processing use the gradio app. 
```
python app.py
```


For running in batch mode use the commandline tool:

```
python run_metalsitepred.py --pdb 2cba.pdb --cubefile test.cube --probefile 2cba_probe.pdb --batch_size 30
```