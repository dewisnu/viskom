# Object Measurement dengan menggunakan kamera eksternal dengan OpenCV dan Streamlit

Proyek ini menunjukkan cara melakukan object measurement dari kamera eksternal menggunakan OpenCV dan menampilkan  video di aplikasi web Streamlit. Ini juga mencakup fungsionalitas untuk mendeteksi objek dan penanda ArUco dalam  video frame.

## Persyaratan

- Python 3.9
- OpenCV
- Streamlit
- NumPy

## Instalasi

Instal pustaka yang diperlukan:

```bash
pip install opencv-python streamlit numpy
```

## File object_detector.py
```bash
import cv2  # Mengimpor pustaka OpenCV untuk pemrosesan gambar dan video

class detectorObj():
    def __init__(self):
        pass  # Metode inisialisasi untuk kelas detectorObj, tidak ada inisialisasi khusus dalam kasus ini

    def detect_objects(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Ubah gambar menjadi skala abu-abu

        # Buat Mask dengan threshold adaptif
        mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Temukan kontur

        objects_contours = []  # Menginisialisasi daftar untuk menyimpan kontur objek yang terdeteksi

        for cnt in contours:  # Iterasi melalui setiap kontur yang ditemukan
            area = cv2.contourArea(cnt)  # Menghitung area kontur
            if area > 2000:  # Memfilter kontur berdasarkan area, hanya menyimpan kontur dengan area lebih dari 2000
                objects_contours.append(cnt)  # Menambahkan kontur yang valid ke daftar objects_contours

        return objects_contours  # Mengembalikan daftar kontur objek yang terdeteksi
```


## File app.py
```bash
import cv2  # Mengimpor pustaka OpenCV untuk pemrosesan gambar dan video
import streamlit as st  # Mengimpor pustaka Streamlit untuk membuat aplikasi web interaktif
from object_detector import *  # Mengimpor semua komponen dari modul object_detector
import numpy as np  # Mengimpor pustaka NumPy untuk operasi numerik
import time  # Mengimpor pustaka time untuk mengatur jeda waktu

st.title("Penangkapan Video dengan OpenCV")  # Menampilkan judul aplikasi di Streamlit

# Membuat input teks di sidebar untuk memasukkan IP kamera eksternal
camera_IP = st.sidebar.text_input("Masukkan IP kamera eksternal", "http://192.168.0.100:8080/video")
cap = cv2.VideoCapture(camera_IP)  # Membuka aliran video dari IP kamera

if st.sidebar.button("Submit"):  # Membuat tombol submit di sidebar
    if camera_IP:  # Jika IP kamera dimasukkan, tampilkan IP
        st.write(camera_IP)
    else:  # Jika tidak, tampilkan pesan kesalahan
        st.sidebar.write("Masukkan teks terlebih dahulu.")

frame_placeholder = st.empty()  # Membuat tempat kosong untuk menampilkan bingkai video
stop_button_pressed = st.button("Stop")  # Membuat tombol stop

if not cap.isOpened():  # Memeriksa apakah video dapat dibuka
    st.error("Error: Tidak bisa membuka file video.")  # Menampilkan pesan kesalahan jika video tidak dapat dibuka
    exit()  # Keluar dari program

# Muat kamus ArUco
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
parameters = cv2.aruco.DetectorParameters()  # Muat parameter detektor ArUco

detector = detectorObj()  # Membuat instance detektor objek

while cap.isOpened():  # Looping selama video terbuka
    ret, img = cap.read()  # Membaca bingkai video

    if not ret:  # Jika bingkai tidak terbaca, keluar dari loop
        st.write("Akhir dari file video telah tercapai.")  # Menampilkan pesan akhir video
        break  # Keluar dari loop

    if img is None or img.size == 0:  # Jika bingkai kosong, tampilkan pesan kesalahan
        st.error("Error: Bingkai yang ditangkap kosong.")  # Menampilkan pesan kesalahan
        continue  # Lanjutkan ke iterasi berikutnya

    # Dapatkan penanda ArUco
    corners, _, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
    if corners:  # Jika penanda terdeteksi
        int_corners = np.int32(corners)  # Mengonversi sudut penanda menjadi integer
        cv2.polylines(img, int_corners, True, (0, 255, 0), 5)  # Menggambar poligon di sekitar penanda

        aruco_perimeter = cv2.arcLength(corners[0], True)  # Menghitung keliling penanda

        pixel_cm_ratio = aruco_perimeter / 20  # Menghitung rasio piksel ke cm

        contours = detector.detect_objects(img)  # Mendeteksi objek dalam bingkai

        for cnt in contours:  # Iterasi melalui setiap kontur objek
            rect = cv2.minAreaRect(cnt)  # Mendapatkan kotak minimum yang mengelilingi kontur
            (x, y), (w, h), angle = rect  # Mendapatkan posisi, ukuran, dan sudut kotak

            object_width = w / pixel_cm_ratio  # Menghitung lebar objek dalam cm
            object_height = h / pixel_cm_ratio  # Menghitung tinggi objek dalam cm

            box = cv2.boxPoints(rect)  # Mendapatkan titik-titik kotak
            box = np.int32(box)  # Mengubah titik-titik kotak menjadi integer

            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)  # Menggambar lingkaran di pusat kotak
            cv2.polylines(img, [box], True, (255, 0, 0), 2)  # Menggambar poligon di sekitar kotak
            cv2.putText(img, f"Width {round(object_width, 1)} cm", (int(x - 100), int(y - 20)),
                        cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)  # Menampilkan teks lebar objek
            cv2.putText(img, f"Height {round(object_height, 1)} cm", (int(x - 100), int(y + 15)),
                        cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)  # Menampilkan teks tinggi objek

    frame_placeholder.image(img, channels="BGR")  # Menampilkan bingkai video di Streamlit

    time.sleep(0.2)  # Jeda selama 0,2 detik

    if stop_button_pressed:  # Jika tombol stop ditekan, keluar dari loop
        break  # Keluar dari loop

cap.release()  # Melepaskan sumber daya video
cv2.destroyAllWindows()  # Menutup semua jendela OpenCV
```

## Cara menjalankan Project
```bash
streamlit run app.py
```