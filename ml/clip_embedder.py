from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from typing import Optional

import albumentations as A
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


class ClipEmbedder:
    # Common object categories for classification
    OBJECT_CATEGORIES = [
        "a photo of a cat",
        "a photo of a dog",
        "a photo of a car",
        "a photo of a person",
        "a photo of a bird",
        "a photo of food",
        "a photo of a building",
        "a photo of nature",
        "a photo of an animal",
    ]
    
    BACKGROUND_CATEGORIES = [
        "indoor background",
        "outdoor background",
        "nature background",
        "urban background",
        "simple background",
    ]

    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
        use_augmentation: bool = True,
        num_augmentations: int = 3,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.use_augmentation = use_augmentation
        self.num_augmentations = num_augmentations
        self._model: Optional[CLIPModel] = None
        self._processor: Optional[CLIPProcessor] = None
        
        # Define augmentation pipeline for test-time augmentation
        if self.use_augmentation:
            self.augmentation = A.Compose([
                A.HorizontalFlip(p=0.5),
                A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
                A.RandomGamma(gamma_limit=(80, 120), p=0.3),
                A.CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), p=0.3),
                A.GaussNoise(var_limit=(10.0, 50.0), p=0.2),
            ])

    def _ensure_model_loaded(self) -> None:
        if self._model is None or self._processor is None:
            self._model = CLIPModel.from_pretrained(self.model_name)
            self._processor = CLIPProcessor.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()

    @lru_cache(maxsize=128)
    def _load_image(self, data_hash: str, data: bytes) -> Image.Image:  # noqa: D401
        # Simple cache by content hash to avoid re-decoding duplicates in batch scenarios.
        return Image.open(BytesIO(data)).convert("RGB")

    def encode_image(self, data: bytes) -> np.ndarray:
        self._ensure_model_loaded()
        assert self._model is not None
        assert self._processor is not None

        # Hash for caching image decoding
        data_hash = str(hash(data))
        pil_image = self._load_image(data_hash, data)

        if self.use_augmentation and self.num_augmentations > 1:
            # Test-time augmentation: create multiple views and average embeddings
            embeddings = []
            
            # Original image
            embedding = self._encode_single_image(pil_image)
            embeddings.append(embedding)
            
            # Augmented versions
            np_image = np.array(pil_image)
            for _ in range(self.num_augmentations - 1):
                augmented = self.augmentation(image=np_image)["image"]
                aug_pil = Image.fromarray(augmented)
                aug_embedding = self._encode_single_image(aug_pil)
                embeddings.append(aug_embedding)
            
            # Average the embeddings for robustness
            embeddings_array = np.vstack(embeddings)
            final_embedding = embeddings_array.mean(axis=0)
            return final_embedding.astype(np.float32)
        else:
            # No augmentation - single pass
            return self._encode_single_image(pil_image)

    def _encode_single_image(self, pil_image: Image.Image) -> np.ndarray:
        """Encode a single PIL image to embedding"""
        self._ensure_model_loaded()
        assert self._model is not None
        assert self._processor is not None

        inputs = self._processor(images=pil_image, return_tensors="pt")
        inputs = {name: tensor.to(self.device) for name, tensor in inputs.items()}

        with torch.no_grad():
            features = self._model.get_image_features(**inputs)
            features = torch.nn.functional.normalize(features, p=2, dim=-1)

        embedding = features.cpu().numpy().astype(np.float32)
        return embedding[0]

    def classify_object(self, data: bytes) -> str:
        """Classify the main object in an image using CLIP text-image similarity with TTA"""
        self._ensure_model_loaded()
        assert self._model is not None
        assert self._processor is not None

        data_hash = str(hash(data))
        pil_image = self._load_image(data_hash, data)

        # Encode text categories once
        text_inputs = self._processor(text=self.OBJECT_CATEGORIES, return_tensors="pt", padding=True)
        text_inputs = {name: tensor.to(self.device) for name, tensor in text_inputs.items()}

        with torch.no_grad():
            text_features = self._model.get_text_features(**text_inputs)
            text_features = torch.nn.functional.normalize(text_features, p=2, dim=-1)

        # Use TTA for classification too
        if self.use_augmentation and self.num_augmentations > 1:
            similarities = []
            
            # Original image
            image_inputs = self._processor(images=pil_image, return_tensors="pt")
            image_inputs = {name: tensor.to(self.device) for name, tensor in image_inputs.items()}
            with torch.no_grad():
                image_features = self._model.get_image_features(**image_inputs)
                image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
                similarity = (image_features @ text_features.T).squeeze(0)
                similarities.append(similarity.cpu().numpy())
            
            # Augmented versions
            np_image = np.array(pil_image)
            for _ in range(self.num_augmentations - 1):
                augmented = self.augmentation(image=np_image)["image"]
                aug_pil = Image.fromarray(augmented)
                aug_inputs = self._processor(images=aug_pil, return_tensors="pt")
                aug_inputs = {name: tensor.to(self.device) for name, tensor in aug_inputs.items()}
                with torch.no_grad():
                    aug_features = self._model.get_image_features(**aug_inputs)
                    aug_features = torch.nn.functional.normalize(aug_features, p=2, dim=-1)
                    aug_similarity = (aug_features @ text_features.T).squeeze(0)
                    similarities.append(aug_similarity.cpu().numpy())
            
            # Average similarities across augmentations
            avg_similarity = np.mean(similarities, axis=0)
            best_match_idx = avg_similarity.argmax()
        else:
            # Single pass without augmentation
            image_inputs = self._processor(images=pil_image, return_tensors="pt")
            image_inputs = {name: tensor.to(self.device) for name, tensor in image_inputs.items()}
            with torch.no_grad():
                image_features = self._model.get_image_features(**image_inputs)
                image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
                similarity = (image_features @ text_features.T).squeeze(0)
                best_match_idx = similarity.argmax().item()
            
        # Return category name without "a photo of a" prefix
        category = self.OBJECT_CATEGORIES[best_match_idx]
        return category.replace("a photo of a ", "").replace("a photo of an ", "").replace("a photo of ", "")

    def classify_background(self, data: bytes) -> str:
        """Classify the background type in an image with TTA"""
        self._ensure_model_loaded()
        assert self._model is not None
        assert self._processor is not None

        data_hash = str(hash(data))
        pil_image = self._load_image(data_hash, data)

        # Encode text categories once
        text_inputs = self._processor(text=self.BACKGROUND_CATEGORIES, return_tensors="pt", padding=True)
        text_inputs = {name: tensor.to(self.device) for name, tensor in text_inputs.items()}

        with torch.no_grad():
            text_features = self._model.get_text_features(**text_inputs)
            text_features = torch.nn.functional.normalize(text_features, p=2, dim=-1)

        # Use TTA for classification
        if self.use_augmentation and self.num_augmentations > 1:
            similarities = []
            
            # Original image
            image_inputs = self._processor(images=pil_image, return_tensors="pt")
            image_inputs = {name: tensor.to(self.device) for name, tensor in image_inputs.items()}
            with torch.no_grad():
                image_features = self._model.get_image_features(**image_inputs)
                image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
                similarity = (image_features @ text_features.T).squeeze(0)
                similarities.append(similarity.cpu().numpy())
            
            # Augmented versions
            np_image = np.array(pil_image)
            for _ in range(self.num_augmentations - 1):
                augmented = self.augmentation(image=np_image)["image"]
                aug_pil = Image.fromarray(augmented)
                aug_inputs = self._processor(images=aug_pil, return_tensors="pt")
                aug_inputs = {name: tensor.to(self.device) for name, tensor in aug_inputs.items()}
                with torch.no_grad():
                    aug_features = self._model.get_image_features(**aug_inputs)
                    aug_features = torch.nn.functional.normalize(aug_features, p=2, dim=-1)
                    aug_similarity = (aug_features @ text_features.T).squeeze(0)
                    similarities.append(aug_similarity.cpu().numpy())
            
            # Average similarities
            avg_similarity = np.mean(similarities, axis=0)
            best_match_idx = avg_similarity.argmax()
        else:
            # Single pass
            image_inputs = self._processor(images=pil_image, return_tensors="pt")
            image_inputs = {name: tensor.to(self.device) for name, tensor in image_inputs.items()}
            with torch.no_grad():
                image_features = self._model.get_image_features(**image_inputs)
                image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
                similarity = (image_features @ text_features.T).squeeze(0)
                best_match_idx = similarity.argmax().item()
            
        return self.BACKGROUND_CATEGORIES[best_match_idx].replace(" background", "")
