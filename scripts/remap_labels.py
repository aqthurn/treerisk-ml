#!/usr/bin/env python3
"""
Re-linka labels antigos para os nomes unificados (arvore_NNNN.txt),
usando o mapeamento.csv. Os labels do makesense estao como cavNN.txt / waNN.txt,
e os do dataset antigo como img_XXXX.txt -- este script renomeia todos para
o nome novo correspondente, SEM tocar no conteudo (as caixas continuam validas
porque os pixels nao mudaram).

Uso:
  python remap_labels.py <pasta_labels_antigos> <pasta_saida> [mapeamento.csv]

Ex:
  python remap_labels.py labels_makesense dataset/labels/all mapeamento.csv
"""
import csv, sys, shutil
from pathlib import Path

if len(sys.argv) < 3:
    print(__doc__); sys.exit(1)

labels_in = Path(sys.argv[1])
labels_out = Path(sys.argv[2]); labels_out.mkdir(parents=True, exist_ok=True)
mapa = Path(sys.argv[3] if len(sys.argv) > 3 else "mapeamento.csv")

# nome_anterior (cav01, img_0019, wa02...) -> stem novo (arvore_0020)
cross = {}
for r in csv.DictReader(open(mapa)):
    if r["nome_anterior"] and r["obs"] != "DUPLICATA":
        cross[r["nome_anterior"]] = Path(r["nome_novo"]).stem

feitos, faltando = 0, []
for ant, novo in cross.items():
    src = labels_in / f"{ant}.txt"
    if src.exists():
        shutil.copy2(src, labels_out / f"{novo}.txt")
        feitos += 1
    else:
        faltando.append(ant)

print(f"Labels re-linkados: {feitos}  ->  {labels_out}")
print(f"Sem .txt (imagem ainda nao anotada ou sem label): {len(faltando)}")
if faltando:
    print("  " + ", ".join(sorted(faltando)[:25]) + (" ..." if len(faltando) > 25 else ""))
