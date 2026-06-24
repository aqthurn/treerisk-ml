import sys, os, yaml, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import CLASSES, DATA_YAML, MODELS_DIR, RESULTS_DIR, MODEL_PATH, RUN_NAME, ROOT, IMAGES_DIR

from ultralytics import YOLO
import torch

parser = argparse.ArgumentParser(description='Treinar modelo YOLOv8')
parser.add_argument('--gpu', action='store_true', help='Usar GPU CUDA se disponivel')
args = parser.parse_args()

print("=" * 60)
print("TREINAMENTO - SAUDE DE ARVORES")
print("=" * 60)

if args.gpu and torch.cuda.is_available():
    device = 0
    batch = 16
    workers = 4
    amp = True
    print(f"\nUsando GPU (CUDA): {torch.cuda.get_device_name(0)}")
elif args.gpu:
    print("\nAVISO: --gpu solicitado mas CUDA nao esta disponivel. Usando CPU.")
    device = 'cpu'
    batch = 4
    workers = 2
    amp = True
else:
    device = 'cpu'
    batch = 4
    workers = 2
    amp = True
    print(f"\nUsando CPU")


def contar_imagens(subpasta):
    p = Path('dataset') / 'images' / subpasta
    if p.exists():
        return len([f for f in p.iterdir() if f.suffix.lower() in {'.jpg', '.jpeg', '.png'}])
    return 0


train_count = contar_imagens('treino')
val_count   = contar_imagens('validacao')
test_count  = contar_imagens('teste')

print(f"\nDATASET:")
print(f"  Treino:    {train_count} imagens")
print(f"  Validacao: {val_count} imagens")
print(f"  Teste:     {test_count} imagens")
print(f"  Total:     {train_count + val_count + test_count} imagens")
print(f"  Classes:   {CLASSES}")

if train_count == 0:
    print("\n❌ NENHUMA IMAGEM DE TREINO ENCONTRADA!")
    print("   Execute: python scripts/preparar_dados.py")
    sys.exit(1)

print("\nCarregando modelo YOLOv8n (pre-treinado)...")
model = YOLO('yolov8n.pt')

# Regera data.yaml com caminho absoluto para funcionar em qualquer maquina
data_config = {
    'path': str(ROOT / 'dataset'),
    'train': 'images/treino',
    'val':   'images/validacao',
    'test':  'images/teste',
    'nc':    len(CLASSES),
    'names': list(CLASSES),
}
DATA_YAML.parent.mkdir(parents=True, exist_ok=True)
with open(DATA_YAML, 'w', encoding='utf-8') as f:
    yaml.dump(data_config, f, default_flow_style=False, allow_unicode=True)
print(f"data.yaml atualizado: {DATA_YAML}")

print("\nIniciando treinamento...")
print("-" * 60)

try:
    results = model.train(
        data=str(DATA_YAML),

        epochs=260,
        imgsz=640,
        batch=batch,
        device=device,
        workers=workers,
        amp=amp,

        patience=50,

        augment=True,
        hsv_h=0.02,
        hsv_s=0.8,
        hsv_v=0.4,
        degrees=15.0,
        translate=0.2,
        scale=0.5,
        shear=5.0,
        flipud=0.5,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.2,

        dropout=0.1,
        label_smoothing=0.1,
        weight_decay=0.0005,

        optimizer='AdamW',
        lr0=0.001,
        lrf=0.01,
        momentum=0.937,

        save=True,
        save_period=10,
        project=str(RESULTS_DIR),
        name=RUN_NAME,
        exist_ok=True,

        val=True,
        verbose=True,
        cos_lr=True,
        warmup_epochs=3,
    )

    print("\n" + "=" * 60)
    print("TREINAMENTO CONCLUIDO!")
    print("=" * 60)

    MODELS_DIR.mkdir(exist_ok=True)
    model.save(str(MODEL_PATH))
    print(f"Modelo salvo em: {MODEL_PATH}")

    print("\nAVALIANDO MODELO...")
    metrics = model.val()

    print("\nMETRICAS FINAIS:")
    print(f"  mAP50-95: {metrics.box.map:.4f}")
    print(f"  mAP50:    {metrics.box.map50:.4f}")
    print(f"  Precisao: {metrics.box.mp:.4f}")
    print(f"  Recall:   {metrics.box.mr:.4f}")

    print("\nMETRICAS POR CLASSE (mAP50-95):")
    print("-" * 40)
    for i, nome in enumerate(CLASSES):
        if i < len(metrics.box.maps):
            valor = metrics.box.maps[i]
            barra = "#" * int(valor * 20)
            print(f"  {i:2d} - {nome:<26}: {valor:.4f} {barra}")

    print(f"\nResultados salvos em: {RESULTS_DIR / RUN_NAME}/")

except Exception as e:
    print(f"\n❌ ERRO DURANTE O TREINAMENTO:")
    print(f"   {e}")
    print("\nVerifique:")
    print("  1. configs/data.yaml esta correto")
    print("  2. Imagens estao nas pastas certas (execute verificar_estrutura_completa.py)")
    print("  3. Pool all/ foi criado e preparar_dados.py foi executado")
