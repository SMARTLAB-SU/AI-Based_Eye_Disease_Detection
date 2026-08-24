# Fundus Split Dataset

[![Kaggle Dataset](https://img.shields.io/badge/Kaggle-Fundus%20Split%20Dataset-blue?style=flat&logo=kaggle)](https://www.kaggle.com/datasets/bhadakwadeutkarsha/fundus-split-dataset)

A pre-split, class-balanced dataset of retinal fundus (eye) images for multi-class classification, covering six conditions: **AMD, Cataract, Dementia, Diabetes, Glaucoma,** and **Normal**.

Direct Kaggle Link: **[Fundus Split Dataset by Bhadakwade Utkarsha](https://www.kaggle.com/datasets/bhadakwadeutkarsha/fundus-split-dataset)**

---

## Dataset Summary

| Metric | Value |
|---|---|
| Total images | 974 unique class-labeled images (1,949 counting the duplicate pooled folder — see [Known Issue](#known-issue-duplicate-split_output-subfolder)) |
| Classes | 6 (AMD, Cataract, Dementia, Diabetes, Glaucoma, Normal) |
| Split | Train 70% / Val 15% / Test 15% (stratified) |
| Random seed | 42 |
| Image format | JPEG |
| Image size | 512×512 px (majority); a subset of raw images are 4096×3072 px — see below |
| Total archive size | ~380 MB |

---

## Class Distribution

| Class | Total | Train | Val | Test |
|---|---|---|---|---|
| AMD | 168 | 117 | 25 | 26 |
| Cataract | 158 | 110 | 24 | 24 |
| Dementia | 158 | 110 | 24 | 24 |
| Diabetes | 158 | 110 | 24 | 24 |
| Glaucoma | 158 | 110 | 24 | 24 |
| Normal | 174 | 121 | 26 | 27 |
| **Total** | **974** | **678** | **147** | **149** |

Split percentages achieved: Train 69.6%, Val 15.1%, Test 15.3%.

A bar chart of this distribution is included at `split_output/class_distribution.png`.

---

## Folder Structure

```
split_output/
├── class_distribution.png     # bar chart of the split
├── split_manifest.json        # per-image path + class + split record
├── split_summary.txt          # plain-text summary (source of the table above)
├── train/
│   ├── AMD/
│   ├── Cataract/
│   ├── Dementia/
│   ├── Diabetes/
│   ├── Glaucoma/
│   └── Normal/
├── val/
│   ├── AMD/ ... Normal/
└── test/
    ├── AMD/ ... Normal/
```

Each class folder contains `.jpg` images. Filenames follow inconsistent conventions inherited from the source data (patient/scan IDs, e.g. `Q201403770_20221216_115216_Color_R_001.jpg`), plus augmented copies.

---

## Data Augmentation

Some images are augmented copies of originals, identifiable by an `_augNNNN` suffix (e.g. `Q101121333_..._aug0018.jpg`). A smaller number of files carry a `clahe` prefix, indicating CLAHE (Contrast Limited Adaptive Histogram Equalization) preprocessing was applied to some source images before augmentation. **If you split by patient/original image rather than by file, be aware augmented duplicates of the same source image could end up in different splits** — check `split_manifest.json` if patient-level leakage matters for your use case.

---

## Image Properties

- The large majority of images are **512×512 px** JPEGs.
- **316 images** (mostly in the `Cataract` class) are original, non-resized captures at **4096×3072 px**. Standardize/resize these before feeding into a fixed-input-size model.

---

## Known Issue: duplicate `split_output` subfolder

Each of `train/`, `val/`, and `test/` contains an extra **`split_output/`** subfolder alongside the six class folders. This is a leftover artifact from the original dataset-generation script (the output directory was nested inside itself when zipped) — it is **not a real 7th class**. It holds a flat, unlabeled pool of images (682 in train, 146 in val, 147 in test) that substantially overlaps with images already present in the proper class folders.

**Recommendation:** delete `train/split_output/`, `val/split_output/`, and `test/split_output/` before training — they are not usable as labeled data and will just double-count/duplicate images if included. This also explains why the Kaggle chart shows "Total: 1949 images" instead of the true labeled count of 974.

```bash
# quick cleanup
find split_output -type d -name split_output -mindepth 2 -exec rm -rf {} +
```

---

## Source / Provenance

Original file paths recorded in `split_manifest.json` indicate the raw data was assembled locally (`.../Desktop/fundus_balanced/...`) before splitting — no public source/citation is embedded in the archive itself.

---

## Suggested Usage

```python
import torchvision.datasets as datasets

train_ds = datasets.ImageFolder("split_output/train")  # after removing split_output/ subfolders
val_ds   = datasets.ImageFolder("split_output/val")
test_ds  = datasets.ImageFolder("split_output/test")
```

---

## License

Licensed under the **MIT License**. Developed by **SMARTLAB-SU**.
