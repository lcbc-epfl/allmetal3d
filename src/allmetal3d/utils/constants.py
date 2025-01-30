weight_path = "/.local/share/allmetal3d/weights/"

model_weights = {
"identity":"/.local/share/allmetal3d/weights/identity_vacancy_geometry_model_2024-03-01_train_lessclasses_skipconnect_hyperparametertuned_geometry_identity_all_g09_300epoch_p01_epoch300.pth",
"water":"/.local/share/allmetal3d/weights/water_0.5A_allmetal_one3dchannel_epoch9.pth",
"metal":"/.local/share/allmetal3d/weights/metal_0.5A_allmetal_one3dchannel_16Abox_filter6_epoch6.pth"
}

download_weights = {
"identity":"https://huggingface.co/spaces/simonduerr/allmetal3d/resolve/main/identity_vacancy_geometry_model_2024-03-01_train_lessclasses_skipconnect_hyperparametertuned_geometry_identity_all_g09_300epoch_p01_epoch300.pth",
"water":"https://huggingface.co/spaces/simonduerr/allmetal3d/resolve/main/water_0.5A_allmetal_one3dchannel_epoch9.pth",
"metal": "https://huggingface.co/spaces/simonduerr/allmetal3d/resolve/main/metal_0.5A_allmetal_one3dchannel_16Abox_filter6_epoch6.pth"
}