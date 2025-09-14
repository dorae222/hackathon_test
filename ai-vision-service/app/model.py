import torch
import torch.nn as nn
import torchvision.models as models
from PIL import Image
import torchvision.transforms as transforms
import logging

logger = logging.getLogger(__name__)


def load_model(model_path, num_labels):
    """
    Loads a trained EfficientNet-B5 model, ensuring architecture matches the state dict.
    """
    device = torch.device(
        "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")

    model = models.efficientnet_b5(weights=None)

    in_features = model.classifier[1].in_features
    logger.info(f"Current model's classifier in_features: {in_features}")
    model.classifier[1] = nn.Linear(in_features, num_labels)

    model.load_state_dict(torch.load(model_path, map_location=device), strict=False)

    model.to(device)
    model.eval()
    return model, device


def predict_image(image_path, model, device, label_names):
    """
    Predicts the class of an image using a sigmoid function for individual probabilities.
    """
    transform = transforms.Compose([
        transforms.Resize((456, 456)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(image_tensor)

        probs = torch.sigmoid(outputs)[0]

        predicted_label = [label_names[probs.argmax()]]

        class_probs = {}
        for i, prob in enumerate(probs):
            # 각 품종의 점수를 0~100 사이의 '닮음 지수'로 변환합니다.
            class_probs[label_names[i]] = float(prob.item()) * 100

        return predicted_label, class_probs
