import sys
import cv2
import imutils
from yoloDet_heliport import YoloTRT
from yoloDet_inisalanı import YoloTRT


# use path for library and engine file
model_heliport = YoloTRT(library="yolov7/build2/libmyplugins.so", engine="yolov7/build2/best.engine", conf=0.75, yolo_ver="v7")
model_inisalani = YoloTRT(library="yolov7/build3/libmyplugins.so", engine="yolov7/build3/best.engine", conf=0.75, yolo_ver="v7")
cap = cv2.VideoCapture(0)  # 0, genellikle bilgisayarın ilk kamerasını temsil eder

def get_region(x, y, width, height):
    region_width = width // 3
    region_height = height // 3
    
    col = x // region_width
    row = y // region_height
    
    return row * 3 + col + 1  # Bölge numarasını 1'den başlayarak döndür



while True:
    ret, frame = cap.read()
    if not ret:
        print("Kamera akışı alınamadı.")
        break

    frame = imutils.resize(frame, width=600)
    detections, t = model.Inference(frame)
    height, width = frame.shape[:2]
    
    for obj in detections:
        class_id = obj['class']
        box = obj['box']
        x1, y1, x2, y2 = box
        
        # nesnenin orta noktaları
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        # nesnenin olduğu bölge
        region = get_region(center_x, center_y, width, height)
        
        # Orta noktayı çizdir
        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
        cv2.putText(frame, f'Center', (center_x - 20, center_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    fps = 1 / t
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    cv2.imshow("Output", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
