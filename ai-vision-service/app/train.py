import json
import os
import random
from pathlib import Path
from typing import Dict, Tuple, List

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Sampler
from torchvision import datasets, models, transforms

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "dog_breed"
MODELS_DIR = APP_DIR.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PTH = Path(os.getenv("MODEL_PTH_PATH", MODELS_DIR / "dog_breed_classifier.pth"))
CLASS_MAP_PATH = Path(os.getenv("CLASS_MAP_PATH", MODELS_DIR / "class_map.json"))
NUM_EPOCHS = int(os.getenv("EPOCHS", "3"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "8"))
LR = float(os.getenv("LR", "1e-4"))
NUM_WORKERS = int(os.getenv("NUM_WORKERS", "0"))  # 0 avoids shm issues in containers
MAX_SAMPLES_PER_CLASS = int(os.getenv("MAX_TRAIN_SAMPLES", "0"))  # 0 means all
USE_PRETRAINED = os.getenv("PRETRAINED", "0") == "1"
FREEZE_BACKBONE = os.getenv("FREEZE_BACKBONE", "0") == "1"


def build_dataloaders() -> Tuple[DataLoader, Dict[str, int]]:
    tfm = transforms.Compose([
        transforms.Resize((456, 456)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    dataset = datasets.ImageFolder(str(DATA_DIR), transform=tfm)
    class_to_idx = dataset.class_to_idx
    if MAX_SAMPLES_PER_CLASS > 0:
        # Build balanced subset indices per class
        per_class: Dict[int, List[int]] = {idx: [] for idx in class_to_idx.values()}
        for i, (_path, label) in enumerate(dataset.samples):
            if len(per_class[label]) < MAX_SAMPLES_PER_CLASS:
                per_class[label].append(i)
        subset_indices: List[int] = []
        for idx_list in per_class.values():
            subset_indices.extend(idx_list)
        random.shuffle(subset_indices)
        sampler = torch.utils.data.SubsetRandomSampler(subset_indices)
        loader = DataLoader(
            dataset,
            batch_size=BATCH_SIZE,
            sampler=sampler,
            num_workers=NUM_WORKERS,
            persistent_workers=bool(NUM_WORKERS > 0),
        )
    else:
        loader = DataLoader(
            dataset,
            batch_size=BATCH_SIZE,
            shuffle=True,
            num_workers=NUM_WORKERS,
            persistent_workers=bool(NUM_WORKERS > 0),
        )
    return loader, class_to_idx


def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    loader, class_to_idx = build_dataloaders()

    num_classes = len(class_to_idx)
    if USE_PRETRAINED:
        try:
            model = models.efficientnet_b5(weights=models.EfficientNet_B5_Weights.DEFAULT)
        except Exception:
            # Fallback if weights cannot be downloaded
            model = models.efficientnet_b5(weights=None)
    else:
        model = models.efficientnet_b5(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    if FREEZE_BACKBONE:
        for name, param in model.named_parameters():
            if not name.startswith("classifier."):
                param.requires_grad = False
    model.to(device)

    # Single-label multi-class classification
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LR)

    model.train()
    for epoch in range(NUM_EPOCHS):
        running_loss = 0.0
        for inputs, labels in loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f"Epoch {epoch+1}/{NUM_EPOCHS} loss: {running_loss/len(loader):.4f}")

    # Save
    MODEL_PTH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), str(MODEL_PTH))
    with open(CLASS_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(class_to_idx, f, ensure_ascii=False, indent=2)
    print(f"Saved model to {MODEL_PTH} and class map to {CLASS_MAP_PATH}")


if __name__ == "__main__":
    train()
