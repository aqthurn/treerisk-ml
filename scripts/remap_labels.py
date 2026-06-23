import shutil
from pathlib import Path

labels = Path("dataset/labels/all")
backup = Path("dataset/labels/all_backup")
if not backup.exists():
    shutil.copytree(labels, backup)
    print(f"backup criado em {backup}")

alterados = 0
for f in sorted(labels.glob("img_*.txt")):
    try:
        num = int(f.stem.split("_")[1])
    except (IndexError, ValueError):
        continue
    if num < 60:          # so o lote novo (originais vao ate 0059)
        continue
    novas, mudou = [], False
    for ln in f.read_text().splitlines():
        p = ln.split()
        if not p:
            continue
        if p[0] == "0":   # cavidade salva errada como cupim
            p[0] = "2"
            mudou = True
        novas.append(" ".join(p))
    if mudou:
        f.write_text("\n".join(novas) + "\n")
        alterados += 1
        print(f"  remapeado: {f.name}")

print(f"\n{alterados} arquivos do lote novo: classe 0 -> 2 (cavidade)")