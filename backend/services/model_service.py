import torch
import time
from typing import List, Dict, Any, Tuple
from PIL import Image
import io
import numpy as np
from backend.core.config import settings


class ModelService:
    """Service for ML model inference (YOLOv8 or Vision Transformer)."""
    
    def __init__(self):
        self.model = None
        self.model_type = settings.MODEL_TYPE
        self.model_path = settings.MODEL_PATH
        self.conf_threshold = settings.MODEL_CONF_THRESHOLD
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def load_model(self):
        """Load the ML model (hot-reloadable)."""
        if self.model is not None:
            return
        
        try:
            if self.model_type == "yolov8":
                from ultralytics import YOLO
                self.model = YOLO(self.model_path)
                self.model.to(self.device)
            elif self.model_type == "vit":
                from transformers import ViTImageProcessor, ViTForImageClassification
                self.processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
                self.model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')
                self.model.to(self.device)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback: use a simpler model
            from ultralytics import YOLO
            self.model = YOLO('yolov8n.pt')
            self.model.to(self.device)
            self.model_type = "yolov8"
    
    def reload_model(self):
        """Hot-reload the model with new configuration."""
        self.model = None
        self.model_type = settings.MODEL_TYPE
        self.model_path = settings.MODEL_PATH
        self.load_model()
    
    def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze an image and return detections."""
        if self.model is None:
            self.load_model()
        
        start_time = time.time()
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            if self.model_type == "yolov8":
                results = self._analyze_with_yolo(image)
            elif self.model_type == "vit":
                results = self._analyze_with_vit(image)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            processing_time = time.time() - start_time
            results['processing_time'] = processing_time
            results['model_type'] = self.model_type
            
            return results
        
        except Exception as e:
            raise RuntimeError(f"Error analyzing image: {e}")
    
    def _analyze_with_yolo(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze image using YOLOv8."""
        results = self.model(image, conf=self.conf_threshold)
        
        detections = []
        labels = []
        confidence_scores = {}
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].tolist()
                label = result.names[class_id]
                
                detections.append({
                    "label": label,
                    "confidence": confidence,
                    "bbox": bbox
                })
                
                if label not in labels:
                    labels.append(label)
                
                if label not in confidence_scores or confidence > confidence_scores[label]:
                    confidence_scores[label] = confidence
        
        return {
            "detections": detections,
            "labels": labels,
            "confidence_scores": confidence_scores,
            "model_version": "yolov8n"
        }
    
    def _analyze_with_vit(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze image using Vision Transformer."""
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
        
        # Get top 5 predictions
        probs = torch.nn.functional.softmax(logits, dim=-1)
        top5_probs, top5_indices = torch.topk(probs, 5)
        
        detections = []
        labels = []
        confidence_scores = {}
        
        for prob, idx in zip(top5_probs[0], top5_indices[0]):
            label = self.model.config.id2label[idx.item()]
            confidence = prob.item()
            
            detections.append({
                "label": label,
                "confidence": confidence,
                "bbox": None
            })
            
            labels.append(label)
            confidence_scores[label] = confidence
        
        return {
            "detections": detections,
            "labels": labels,
            "confidence_scores": confidence_scores,
            "model_version": "vit-base-patch16-224"
        }


# Global model service instance
model_service = ModelService()
