import sys
from pathlib import Path

# Garante UTF-8 no terminal Windows (evita erro ao printar acentos/emojis)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent

CLASSES = [
    'cupim',
    'poda',
    'cavidade',
    'raiz_exposta',
    'decomposicao',
    'fungo',
    'levantamento_pavimento',
    'inclinacao',
]

IMAGES_DIR  = ROOT / 'dataset' / 'images'
LABELS_DIR  = ROOT / 'dataset' / 'labels'
DATA_YAML   = ROOT / 'configs' / 'data.yaml'
MODELS_DIR  = ROOT / 'modelos'
MODEL_PATH  = MODELS_DIR / 'modelo_arvores.pt'
RESULTS_DIR = ROOT / 'resultados'
RUN_NAME    = 'treino_arvores'
