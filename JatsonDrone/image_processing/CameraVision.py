import math
import threading
import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

from drone_data.Datas import Datas


class CameraVision(threading.Thread):
    def __init__(self, drone):
        threading.Thread.__init__(self)
        self.hedef_find=False
        self.find_lat=None
        self.find_lon = None
        """
        self.cap = cv2.VideoCapture(0)
        desired_fps = 30
        self.cap.set(cv2.CAP_PROP_FPS, desired_fps)
        self.width, self.height = 1920, 1080
        
        ret, image = self.cap.read()
        if not ret:
            print("Kameradan görüntü alınamadı")
            return
        self.oran = (self.height / image.shape[0])
        self.ekran_orta_x,self.ekran_orta_y = self.width/2,self.height/2"""
        
        self.model = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_ssd')
        self.utils = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_ssd_processing_utils')

        a = torch.load('/content/drive/MyDrive/ATeknofest/epoch_0.pt')
        self.model.load_state_dict(a["model"])
        self.model = self.model.to('cuda')
        self.model.eval()
        my_classes = {
            0: 'heliport',
            1: 'class2'
        }

        self.transform = transforms.Compose([
        self.transforms.ToTensor(),
        self.transforms.Resize((300, 300)),
        self.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def change_model(self,model):
        if model == "hedef":
            """ hedef alan için eğitilen model"""
        else:
            """hareketli alan için eğitilen model"""
            

    def ters_haversine(self, lon_u, yön):
        heading = self.loc.heading
        lat1 = self.loc.lat
        lon1 = self.loc.lng
        R = 6371.0
        c = lon_u / (R * 1000)
        a = math.tan(c / 2) ** 2 / (1 + math.tan(c / 2) ** 2)
        dlon = math.asin(2 * math.sqrt(a / (math.cos(math.radians(lat1)) ** 2)))
        dlat = math.asin(math.sqrt(a)) * 2

        if 0 < heading < 90:
            lon2 = math.radians(lon1) - dlon
            lat2 = math.radians(lat1) + dlat
        elif 90 < heading < 180:
            lon2 = math.radians(lon1) + dlon
            lat2 = math.radians(lat1) + dlat
        elif 180 < heading < 270:
            lon2 = math.radians(lon1) + dlon
            lat2 = math.radians(lat1) - dlat
        elif 270 < heading:
            lon2 = math.radians(lon1) - dlon
            lat2 = math.radians(lat1) - dlat
        elif heading == 0:
            if yön > 0:
                lon2 = math.radians(lon1) - dlon
                lat2 = math.radians(lat1) + dlat
            else:
                lon2 = math.radians(lon1) - dlon
                lat2 = math.radians(lat1) - dlat
        elif heading == 90:
            if yön > 0:
                lon2 = math.radians(lon1) + dlon
                lat2 = math.radians(lat1) + dlat
            else:
                lon2 = math.radians(lon1) - dlon
                lat2 = math.radians(lat1) + dlat
        elif heading == 180:
            if yön > 0:
                lon2 = math.radians(lon1) + dlon
                lat2 = math.radians(lat1) - dlat
            else:
                lon2 = math.radians(lon1) + dlon
                lat2 = math.radians(lat1) + dlat
        elif heading == 270:
            if yön > 0:
                lon2 = math.radians(lon1) + dlon
                lat2 = math.radians(lat1) - dlat
            else:
                lon2 = math.radians(lon1) - dlon
                lat2 = math.radians(lat1) - dlat

        return math.degrees(lat2), math.degrees(lon2)

    def konum_hesapla(self, yukseklik, alan, orta_nokta):
        dikey_aci_ileri = 25
        dikey_aci_geri = 25
        yatay_aci_sol = 70
        yatay_aci_sağ = 10

        yatay_pixsel = round((1920 * math.tan(math.radians(yatay_aci_sağ))) / (
                math.tan(math.radians(yatay_aci_sol)) + math.tan(math.radians(yatay_aci_sağ))))
        dikey_pixsel = round((1080 * math.tan(math.radians(dikey_aci_geri))) / (
                math.tan(math.radians(dikey_aci_ileri)) + math.tan(math.radians(dikey_aci_geri))))

        tan_y = (1080 - dikey_pixsel - alan[1]) * math.tan(math.radians(dikey_aci_ileri)) / (1080 - dikey_pixsel)
        tan_x = (1920 - yatay_pixsel - alan[0]) * math.tan(math.radians(yatay_aci_sol)) / (1920 - yatay_pixsel)
        gercek_uzaklik_yatay = tan_x * (math.sqrt(pow((yukseklik * math.tan(math.radians(dikey_aci_ileri)) * (
                1080 - dikey_pixsel - alan[1]) / (1080 - dikey_pixsel)), 2) + pow(yukseklik, 2)))
        gercek_uzaklik_dikey = tan_y * (math.sqrt(pow((yukseklik * math.tan(math.radians(yatay_aci_sol)) * (
                1920 - yatay_pixsel - alan[0]) / (1920 - yatay_pixsel)), 2) + pow(yukseklik, 2)))

        sağ = 1
        sol = -1
        if orta_nokta[0] >= alan[0]:
            yön = sağ
        else:
            yön = sol
        return self.ters_haversine(gercek_uzaklik_dikey, yön)

    def run(self):

        while True:
            ret, image = self.cap.read()
            if not ret:
                print("Kare alınamadı")
                break
            # OpenCV formatında okunan frame'i PIL formatına dönüştür
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            x = transform(image).unsqueeze(0)
            
            # Modeli kullanarak tahmin yap
            with torch.no_grad():
                x = x.to('cuda')
                detections = model(x)
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

                if not self.hedef_find:
                    self.find_lat, self.find_lon = Thread(target=self.konum_hesapla(self.loc.alt, (x_center * self.oran, y_center * self.oran),
                                                                    (self.width, self.height)))
                    self.hedef_find = True
                        