# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 19:11:28 2024

@author: VuralBayraklii
"""

import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

model = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_ssd')
utils = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_ssd_processing_utils')

a = torch.load('/content/drive/MyDrive/ATeknofest/epoch_0.pt')
model.load_state_dict(a["model"])
model = model.to('cuda')
model.eval()
my_classes = {
    0: 'heliport',
    1: 'class2'
}

video_path = '/content/test.mp4'
cap = cv2.VideoCapture(video_path)

# Video kaydedici ayarları
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output_video.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize((300, 300)),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
i = 0
while cap.isOpened():

    ret, frame = cap.read()
    height, width, _ = frame.shape

    if not ret:
        break

    # OpenCV formatında okunan frame'i PIL formatına dönüştür
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    x = transform(image).unsqueeze(0)

    # Modeli kullanarak tahmin yap
    with torch.no_grad():
        x = x.to('cuda')
        detections = model(x)

    # Tahminleri işleyin
    results_per_input = utils.decode_results(detections)
    best_results_per_input = [utils.pick_best(results, 0.40) for results in results_per_input]

    # Tahmin edilen nesneleri çizin
    for result in best_results_per_input:
        bboxes, classes, scores = result
        print(bboxes)
        x_min, y_min, x_max, y_max = bboxes[0]
        x_min_new = int(x_min * width)
        y_min_new = int(y_min * height)
        x_max_new = int(x_max * width)
        y_max_new = int(y_max * height)

        bbox_new = [x_min_new, y_min_new, x_max_new, y_max_new]
        x_center = (x_min_new + x_max_new) // 2
        y_center = (y_min_new + y_max_new) // 2
        print("bboxnew", bbox_new)
        print("width, height", width, height)
        print(x_center, y_center)

        for bbox, cls, score in zip(bboxes, classes, scores):
            print(cls, score)
            if score < 0.40:
                continue
            x_min, y_min, x_max, y_max = bbox
            x_min = int(x_min * frame.shape[1])
            y_min = int(y_min * frame.shape[0])
            x_max = int(x_max * frame.shape[1])
            y_max = int(y_max * frame.shape[0])
            cv2.circle(frame, (x_center, y_center), radius=6, color=(255, 0, 0), thickness=-1)
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            label = f"{my_classes[cls-1]}: {score:.2f}"
            cv2.putText(frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if i == 400:
      break
    # İşlenmiş frame'i kaydedin
    out.write(frame)
    i += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırakın
cap.release()
out.release()