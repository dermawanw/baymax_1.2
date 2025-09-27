import cv2

def main():
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    if not cap.isOpened():
        raise RuntimeError("Webcam tidak terbuka. Cek permission atau device ID.")

    print("Tekan 'q' di jendela video untuk keluar.")
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Gagal baca frame dari kamera.")
            break

        # opsional: flip biar mirror
        frame = cv2.flip(frame, 1)

        cv2.imshow("Baymax Vision - Webcam Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
