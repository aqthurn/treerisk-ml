import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import IMAGES_DIR, LABELS_DIR, CLASSES

print("=" * 60)
print("VERIFICANDO ESTRUTURA DO DATASET")
print("=" * 60)

IMG_EXTS = {'.jpg', '.jpeg', '.png'}

# Pool mestre
pool_imgs = IMAGES_DIR / 'all'
pool_lbls = LABELS_DIR / 'all'

if pool_imgs.exists():
    imgs = [f for f in pool_imgs.iterdir() if f.suffix.lower() in IMG_EXTS]
    lbls = [f for f in pool_lbls.iterdir() if f.suffix == '.txt'] if pool_lbls.exists() else []
    print(f"\nPOOL MESTRE (all/):")
    print(f"  Imagens: {len(imgs)}")
    print(f"  Labels:  {len(lbls)}")
    sem_label = [f.name for f in imgs if not (pool_lbls / f"{f.stem}.txt").exists()]
    if sem_label:
        print(f"  Sem label ({len(sem_label)}): {', '.join(sorted(sem_label)[:10])}" +
              (" ..." if len(sem_label) > 10 else ""))
else:
    print(f"\n[!] Pool all/ nao encontrado: {pool_imgs}")
    print("    Execute: python scripts/preparar_dados.py para gerar o split apos criar o pool.")

# Splits
subpastas = ['treino', 'validacao', 'teste']
total_imgs = 0

print("\nSPLITS:")
for pasta in subpastas:
    img_path = IMAGES_DIR / pasta
    lbl_path = LABELS_DIR / pasta

    if img_path.exists():
        imagens = [f for f in img_path.iterdir() if f.suffix.lower() in IMG_EXTS]
        labels  = list(lbl_path.glob('*.txt')) if lbl_path.exists() else []
        print(f"\n  {pasta}/")
        print(f"    Imagens: {len(imagens)}")
        print(f"    Labels:  {len(labels)}")
        total_imgs += len(imagens)
    else:
        print(f"\n  {pasta}/  [NAO ENCONTRADA]")

print("\n" + "=" * 60)
print(f"Total de imagens nos splits: {total_imgs}")
if total_imgs == 0:
    print("[!] Nenhuma imagem nos splits. Execute: python scripts/preparar_dados.py")
print("=" * 60)
