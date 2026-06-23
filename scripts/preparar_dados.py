"""
Divide o pool mestre (dataset/images/all/ + dataset/labels/all/) em
treino/validacao/teste usando cópia (nunca move o all/).

Split: 70% treino / 20% validação / 10% teste (estratificado por classe
dominante de cada imagem para equilibrar a distribuição).

Uso: python scripts/preparar_dados.py
     (executar a partir da raiz do projeto)
"""
import sys, shutil, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import IMAGES_DIR, LABELS_DIR, CLASSES

from sklearn.model_selection import train_test_split

TRAIN_RATIO = 0.70
VAL_RATIO   = 0.20
# TEST_RATIO = 0.10  (o que sobra)
SEED = 42

IMG_EXTS = {'.jpg', '.jpeg', '.png'}

# ── 1. Lê o pool mestre ──────────────────────────────────────────────────────
pool_imgs = IMAGES_DIR / 'all'
pool_lbls = LABELS_DIR / 'all'

if not pool_imgs.exists():
    print(f"❌ Pool mestre não encontrado: {pool_imgs}")
    print("   Execute primeiro: montar_pool.py  (ou copie as imagens para dataset/images/all/)")
    sys.exit(1)

imagens = sorted([f for f in pool_imgs.iterdir() if f.suffix.lower() in IMG_EXTS])
print(f"Pool mestre: {len(imagens)} imagens em {pool_imgs}")

if not imagens:
    print("❌ Nenhuma imagem encontrada no pool mestre.")
    sys.exit(1)

# ── 2. Determina a classe dominante de cada imagem (para estratificação) ─────
def classe_dominante(stem):
    txt = pool_lbls / f"{stem}.txt"
    if not txt.exists():
        return -1  # sem label → classe especial "sem_anotação"
    contagem = collections.Counter()
    for linha in txt.read_text().splitlines():
        linha = linha.strip()
        if linha:
            contagem[int(linha.split()[0])] += 1
    return contagem.most_common(1)[0][0] if contagem else -1

classes_dom = [classe_dominante(img.stem) for img in imagens]

# ── 3. Separa imagens sem label (não entram no split estratificado) ───────────
sem_label = [img for img, c in zip(imagens, classes_dom) if c == -1]
com_label = [img for img, c in zip(imagens, classes_dom) if c != -1]
classes_com = [c for c in classes_dom if c != -1]

if sem_label:
    print(f"[!] {len(sem_label)} imagem(ns) sem label - ficam no pool mas nao entram no split:")
    for f in sem_label:
        print(f"   {f.name}")

# ── 4. Split estratificado (com fallback para classes raras) ─────────────────
import collections as _col

# Agrupa classes com < 2 imagens num bucket "raro" para não quebrar o stratify
contagem_cls = _col.Counter(classes_com)
classes_para_stratify = [c if contagem_cls[c] >= 2 else -2 for c in classes_com]

val_test_ratio = 1.0 - TRAIN_RATIO

try:
    train_imgs, tmp_imgs, train_cls, tmp_cls = train_test_split(
        com_label, classes_para_stratify,
        test_size=val_test_ratio,
        stratify=classes_para_stratify,
        random_state=SEED,
    )
    test_fraction = (1.0 - TRAIN_RATIO - VAL_RATIO) / val_test_ratio
    val_imgs, test_imgs = train_test_split(
        tmp_imgs,
        test_size=test_fraction,
        stratify=tmp_cls,
        random_state=SEED,
    )
    print("Split estratificado (classes raras agrupadas).")
except ValueError as e:
    print(f"[!] Stratify falhou ({e}). Usando split aleatorio.")
    train_imgs, tmp_imgs = train_test_split(com_label, test_size=val_test_ratio, random_state=SEED)
    test_fraction = (1.0 - TRAIN_RATIO - VAL_RATIO) / val_test_ratio
    val_imgs, test_imgs = train_test_split(tmp_imgs, test_size=test_fraction, random_state=SEED)

print(f"\nSplit:")
print(f"  Treino:    {len(train_imgs)} imagens")
print(f"  Validação: {len(val_imgs)} imagens")
print(f"  Teste:     {len(test_imgs)} imagens")

# ── 5. Limpa splits antigos e copia do pool ──────────────────────────────────
splits = {'treino': train_imgs, 'validacao': val_imgs, 'teste': test_imgs}

for nome, imgs in splits.items():
    img_dest = IMAGES_DIR / nome
    lbl_dest = LABELS_DIR / nome

    # Limpa split antigo
    if img_dest.exists():
        shutil.rmtree(img_dest)
    if lbl_dest.exists():
        shutil.rmtree(lbl_dest)
    img_dest.mkdir(parents=True)
    lbl_dest.mkdir(parents=True)

    sem_par = []
    for img in imgs:
        shutil.copy2(img, img_dest / img.name)
        lbl_src = pool_lbls / f"{img.stem}.txt"
        if lbl_src.exists():
            shutil.copy2(lbl_src, lbl_dest / lbl_src.name)
        else:
            sem_par.append(img.name)

    if sem_par:
        print(f"[!] {nome}: {len(sem_par)} imagem(ns) copiada(s) sem label correspondente")

# ── 6. Distribuição por classe ───────────────────────────────────────────────
print("\n" + "=" * 55)
print("Distribuição por classe (instâncias nos splits):")
print(f"{'Classe':<28} {'Treino':>7} {'Val':>5} {'Teste':>6}")
print("-" * 55)

def contar_instancias(split_name):
    lbl_dir = LABELS_DIR / split_name
    contagem = collections.Counter()
    if lbl_dir.exists():
        for txt in lbl_dir.glob('*.txt'):
            for linha in txt.read_text().splitlines():
                linha = linha.strip()
                if linha:
                    contagem[int(linha.split()[0])] += 1
    return contagem

ct = {s: contar_instancias(s) for s in ['treino', 'validacao', 'teste']}
for idx, nome_cls in enumerate(CLASSES):
    t = ct['treino'].get(idx, 0)
    v = ct['validacao'].get(idx, 0)
    e = ct['teste'].get(idx, 0)
    alerta = "  <- RARO" if (t + v + e) < 10 else ""
    print(f"  {idx} {nome_cls:<26} {t:>7} {v:>5} {e:>6}{alerta}")

print("=" * 55)
print("OK - Dataset dividido. Execute verificar_estrutura_completa.py para conferir.")
