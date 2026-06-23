"""
Detecção em tempo real via webcam.
Não funciona no WSL (sem acesso à webcam). Executar no Windows nativo.
Uso: python scripts/deteccao_webcam.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MODEL_PATH

from ultralytics import YOLO
import cv2

if not MODEL_PATH.exists():
    print(f"❌ Modelo não encontrado: {MODEL_PATH}")
    print("   Execute o treinamento primeiro: python scripts/treinar_otimizado.py")
    sys.exit(1)

print(f"Carregando modelo: {MODEL_PATH}")
model = YOLO(str(MODEL_PATH))

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Não foi possível abrir a webcam!")
    sys.exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("\nDETECCAO EM TEMPO REAL")
print("=" * 40)
print("  'q' — sair")
print("  's' — salvar frame atual")
print("=" * 40)

confianca_minima = 0.5
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    results = model(frame, conf=confianca_minima)
    annotated_frame = results[0].plot()

    num_deteccoes = len(results[0].boxes) if results[0].boxes else 0
    cv2.putText(annotated_frame, f"Conf: {confianca_minima:.2f} | Det: {num_deteccoes}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Deteccao de Arvores', annotated_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        filename = f"captura_{frame_count}.jpg"
        cv2.imwrite(filename, annotated_frame)
        print(f"Captura salva: {filename}")

cap.release()
cv2.destroyAllWindows()
print("\n✅ Webcam liberada!")
