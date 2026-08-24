# Dataset Overview & Preprocessing Guide

## 1. Dataset Source
- **Primary Source**: Multi-class ocular fundus image datasets (Ocular Disease Intelligent Recognition, Glaucoma & Diabetic Retinopathy public benchmarks).
- **Disease Categories**: AMD, Cataract, Dementia (Retinal Microvascular Signs), Diabetic Retinopathy (Diabetes), Glaucoma, and Normal baseline controls.

## 2. Image Format & Specs
- **File Format**: Standardized RGB images (`.png`, `.jpg`).
- **Input Dimensions**: Resized to $640 \times 640$ tensor grid.
- **Normalization**: Normalized using standard ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`.

## 3. Preprocessing Pipeline
1. **Quality Audit**: Filtering out blurry or severely occluded fundus photographs.
2. **Crop & Rescale**: Centering the optic disc / macular region and resizing to $640 \times 640$.
3. **Data Augmentation**: Random horizontal flips, brightness adjustment, and rotation ($\pm 15^\circ$).

## 4. Subdirectories
- `Report/`: Contains statistical reports, class distribution metrics, and exploratory data analysis (EDA) notebooks.
