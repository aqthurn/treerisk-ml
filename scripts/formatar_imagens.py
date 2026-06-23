"""
Formata imagens novas para o pool do dataset.

O que faz:
  1. Auto-orienta via tag EXIF (evita caixas desalinhadas no treino)
  2. Converte HEIC/PNG/WEBP/BMP -> JPG
  3. Renomeia para img_NNNN.jpg continuando a numeracao do pool
  4. Descarta duplicatas por conteudo (MD5 dos pixels)
  5. Registra tudo em mapeamento.csv

Uso:
  python scripts/formatar_imagens.py <pasta_de_entrada>
  python scripts/formatar_imagens.py <pasta_de_entrada> --inicio 50

HEIC: requer 'pip install pillow-heif'. Se nao instalado, arquivos .heic sao pulados com aviso.
"""

import sys, hashlib, csv, argparse
from pathlib import Path
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ROOT, IMAGES_DIR

POOL_DIR     = IMAGES_DIR / 'all'
MAPEAMENTO   = ROOT / 'mapeamento.csv'
QUALIDADE_JPG = 95

EXTENSOES = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    EXTENSOES.add('.heic')
    EXTENSOES.add('.heif')
    _heic_ok = True
except ImportError:
    _heic_ok = False


def _md5_pixels(img: Image.Image) -> str:
    return hashlib.md5(img.tobytes()).hexdigest()


def _proximo_numero(pool_dir: Path) -> int:
    numeros = [
        int(f.stem[4:])
        for f in pool_dir.glob('img_*.jpg')
        if f.stem[4:].isdigit()
    ]
    return max(numeros, default=0) + 1


def _hashes_existentes(pool_dir: Path) -> dict[str, str]:
    """Retorna {md5: nome_do_arquivo} para as imagens ja no pool."""
    hashes = {}
    for p in pool_dir.glob('img_*.jpg'):
        try:
            with Image.open(p) as img:
                hashes[_md5_pixels(img)] = p.name
        except Exception:
            pass
    return hashes


def _abrir_e_orientar(src: Path) -> Image.Image | None:
    try:
        img = Image.open(src)
        img = ImageOps.exif_transpose(img)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except Exception as e:
        print(f"  AVISO: nao foi possivel processar {src.name}: {e}")
        return None


def _carregar_mapeamento_existente() -> list[dict]:
    if not MAPEAMENTO.exists():
        return []
    with open(MAPEAMENTO, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _salvar_mapeamento(linhas: list[dict]) -> None:
    campos = ['original', 'nome_anterior', 'nome_novo', 'obs']
    with open(MAPEAMENTO, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)


def formatar(pasta_entrada: Path, inicio: int | None = None) -> None:
    if not pasta_entrada.exists():
        print(f"ERRO: pasta nao encontrada: {pasta_entrada}")
        sys.exit(1)

    POOL_DIR.mkdir(parents=True, exist_ok=True)

    if not _heic_ok:
        print("AVISO: pillow-heif nao instalado — arquivos .heic serao ignorados.")
        print("       Para suporte HEIC: pip install pillow-heif\n")

    print(f"Pool destino : {POOL_DIR}")
    print(f"Fonte        : {pasta_entrada}")

    candidatos = sorted(
        p for p in pasta_entrada.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSOES
    )

    if not candidatos:
        print("Nenhuma imagem encontrada na pasta de entrada.")
        return

    print(f"Imagens encontradas: {len(candidatos)}\n")
    print("Carregando hashes do pool existente...")
    hashes = _hashes_existentes(POOL_DIR)
    print(f"  {len(hashes)} imagens ja no pool\n")

    contador = inicio if inicio is not None else _proximo_numero(POOL_DIR)
    mapeamento = _carregar_mapeamento_existente()

    adicionadas = 0
    duplicatas  = 0
    erros       = 0

    for src in candidatos:
        img = _abrir_e_orientar(src)
        if img is None:
            erros += 1
            continue

        md5 = _md5_pixels(img)

        if md5 in hashes:
            print(f"  DUP  {src.name} -> ja existe como {hashes[md5]}")
            mapeamento.append({
                'original':     str(src),
                'nome_anterior': src.name,
                'nome_novo':    hashes[md5],
                'obs':          'DUPLICATA',
            })
            duplicatas += 1
            continue

        nome_novo = f'img_{contador:04d}.jpg'
        destino   = POOL_DIR / nome_novo

        img.save(destino, 'JPEG', quality=QUALIDADE_JPG, optimize=True)
        hashes[md5] = nome_novo

        mapeamento.append({
            'original':     str(src),
            'nome_anterior': src.name,
            'nome_novo':    nome_novo,
            'obs':          '',
        })

        print(f"  OK   {src.name} -> {nome_novo}")
        adicionadas += 1
        contador += 1

    _salvar_mapeamento(mapeamento)

    print(f"\n{'='*50}")
    print(f"Adicionadas : {adicionadas}")
    print(f"Duplicatas  : {duplicatas} (ignoradas)")
    print(f"Erros       : {erros}")
    print(f"Proximo num : img_{contador:04d}.jpg")
    print(f"mapeamento.csv atualizado: {MAPEAMENTO}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Formata imagens para o pool do dataset.')
    parser.add_argument('entrada', type=Path, help='Pasta com as imagens brutas')
    parser.add_argument('--inicio', type=int, default=None,
                        help='Numero inicial da numeracao (padrao: proximo disponivel no pool)')
    args = parser.parse_args()
    formatar(args.entrada, args.inicio)
