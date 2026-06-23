"""
Testa o modelo treinado em uma imagem e exibe as detecções.
Uso: python scripts/testar_imagem.py [caminho_da_imagem]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MODEL_PATH, IMAGES_DIR

from ultralytics import YOLO
import cv2

# Permite passar o caminho da imagem como argumento
if len(sys.argv) > 1:
    imagem_teste = Path(sys.argv[1])
else:
    # Pega a primeira imagem disponível no split de teste
    teste_dir = IMAGES_DIR / 'teste'
    imgs = sorted(teste_dir.glob('*.jpg')) + sorted(teste_dir.glob('*.jpeg')) + sorted(teste_dir.glob('*.png'))
    if not imgs:
        print(f"❌ Nenhuma imagem encontrada em {teste_dir}")
        print("   Passe o caminho como argumento: python scripts/testar_imagem.py caminho/imagem.jpg")
        sys.exit(1)
    imagem_teste = imgs[0]

if not imagem_teste.exists():
    print(f"❌ Imagem não encontrada: {imagem_teste}")
    sys.exit(1)

if not MODEL_PATH.exists():
    print(f"❌ Modelo não encontrado: {MODEL_PATH}")
    print("   Execute o treinamento primeiro: python scripts/treinar_otimizado.py")
    sys.exit(1)

print(f"Modelo:  {MODEL_PATH}")
print(f"Imagem:  {imagem_teste}")

model = YOLO(str(MODEL_PATH))
results = model(str(imagem_teste), conf=0.25)

for r in results:
    im_array = r.plot()
    cv2.imshow('Deteccao', im_array)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

saida = Path('resultado_deteccao.jpg')
results[0].save(str(saida))
print(f"✅ Resultado salvo em: {saida}")
