# Gemiye-Kalkis-Inis-Yapabilen-Akilli-Muhimmatli-DIKY-VTOL-IHA
Otonom uçuşun esnekliği için yeni uçuş modları geliştirdim.
Kamera görüntüsü üzerinden hedef nesnelerin belirlenmesi üzerine çalıştım.
Lidar sensör gibi uzaklık ölçen sensörleri kullanmadan aranan hedeflerin
konumlarını hesaplayan algoritma geliştirdim.
Step motorlar kullanarak bir araç takip algoritması geliştirdim. Bu sayede İHA ile
yer istasyonu arasında iletişimin süreklilik kazanmasını sağladım.
Gazebo ve ROS kullanarak simülasyon ve test çalışmaları yürüttüm.
Otonom kontrol alanında en çok kullanılan MAVLink ktüphanesinde yeni uçuş
modu ekleyerek İHA aracımız için daha performanslı bir uçuş gerçekleştirdim.
Görüntü işleme çalışmamız için YOLOv7'de ve Inceptionv3 kullanarak model
eğittim.
