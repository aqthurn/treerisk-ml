"""
Remapeia indices de classe nos arquivos .txt YOLO.

Necessario quando a lista de classes muda de ordem ou tamanho.
Classes removidas do novo esquema tem suas linhas apagadas dos .txt.

Esquema antigo (8 classes):
  0 cupim  1 poda  2 cavidade  3 raiz_exposta
  4 decomposicao  5 fungo  6 levantamento_pavimento  7 inclinacao

Esquema novo (4 classes, alfabetico):
  0 cavidade  1 levantamento_pavimento  2 poda  3 raiz_exposta

Uso:
  python scripts/remapear_indices.py                  # opera em dataset/labels/all/
  python scripts/remapear_indices.py --dry-run        # mostra o que faria sem alterar nada
  python scripts/remapear_indices.py --pasta outra/   # pasta customizada
"""

import sys, argparse, shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import LABELS_DIR

# None = remover a linha do .txt
MAPA = {
    0: None,  # cupim              → removida
    1: 2,     # poda               → 2
    2: 0,     # cavidade           → 0
    3: 3,     # raiz_exposta       → 3 (nao mudou)
    4: None,  # decomposicao       → removida
    5: None,  # fungo              → removida
    6: 1,     # levantamento_pavimento → 1
    7: None,  # inclinacao         → removida
}


def remapear_arquivo(txt: Path, dry_run: bool) -> tuple[int, int]:
    """Retorna (linhas_mantidas, linhas_removidas)."""
    linhas = txt.read_text(encoding='utf-8').splitlines()
    novas = []
    removidas = 0

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        partes = linha.split()
        idx_antigo = int(partes[0])
        idx_novo = MAPA.get(idx_antigo)

        if idx_novo is None:
            removidas += 1
            continue

        partes[0] = str(idx_novo)
        novas.append(' '.join(partes))

    if not dry_run:
        txt.write_text('\n'.join(novas) + ('\n' if novas else ''), encoding='utf-8')

    return len(novas), removidas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pasta', type=Path, default=LABELS_DIR / 'all',
                        help='Pasta com os .txt a remapear (padrao: dataset/labels/all)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Mostra o que faria sem alterar nenhum arquivo')
    parser.add_argument('--ate', type=int, default=None, metavar='N',
                        help='Processa somente img_0001 ate img_NNNN (ex: --ate 79 para so o dataset antigo)')
    args = parser.parse_args()

    pasta: Path = args.pasta
    dry = args.dry_run

    if not pasta.exists():
        print(f"ERRO: pasta nao encontrada: {pasta}")
        sys.exit(1)

    todos = sorted(pasta.glob('*.txt'))
    if args.ate is not None:
        txts = [t for t in todos if t.stem.startswith('img_') and
                t.stem[4:].isdigit() and int(t.stem[4:]) <= args.ate]
        print(f"Filtro --ate {args.ate}: {len(txts)} de {len(todos)} arquivos serao processados\n")
    else:
        txts = todos
    if not txts:
        print(f"Nenhum .txt encontrado em {pasta}")
        sys.exit(0)

    if not dry:
        backup = pasta.parent / f'all_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copytree(pasta, backup)
        print(f"Backup criado em: {backup}\n")

    modo = '[DRY-RUN] ' if dry else ''
    print(f"{modo}Remapeando {len(txts)} arquivos em {pasta}\n")

    total_mantidas = 0
    total_removidas = 0

    for txt in txts:
        mantidas, removidas = remapear_arquivo(txt, dry)
        total_mantidas  += mantidas
        total_removidas += removidas
        if removidas:
            print(f"  {txt.name}: {mantidas} boxes mantidas, {removidas} removidas")

    print(f"\n{'='*50}")
    print(f"Boxes mantidas : {total_mantidas}")
    print(f"Boxes removidas: {total_removidas} (classes fora do novo esquema)")
    if dry:
        print("\nNada foi alterado (--dry-run). Remova a flag para aplicar.")
    else:
        print(f"\nFeito. Para desfazer: copie o backup de volta para {pasta}")


if __name__ == '__main__':
    main()
