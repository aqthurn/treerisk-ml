import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import CLASSES, RESULTS_DIR, RUN_NAME

import pandas as pd
import matplotlib.pyplot as plt

resultados_dir = RESULTS_DIR / RUN_NAME

if not resultados_dir.exists():
    print(f"❌ Pasta de resultados não encontrada: {resultados_dir}")
    print("   Execute o treinamento primeiro: python scripts/treinar_otimizado.py")
    sys.exit(1)

results_file = resultados_dir / 'results.csv'
if not results_file.exists():
    print(f"❌ Arquivo results.csv não encontrado em {resultados_dir}")
    sys.exit(1)

df = pd.read_csv(results_file)
df.columns = df.columns.str.strip()

print("=" * 60)
print("ANALISE DOS RESULTADOS DO TREINAMENTO")
print("=" * 60)
print(f"  Total de epocas: {len(df)}")
print(f"  Classes ({len(CLASSES)}): {', '.join(CLASSES)}")

best_mAP50    = df['metrics/mAP50(B)'].max()
best_ep_50    = df['metrics/mAP50(B)'].idxmax()
best_mAP      = df['metrics/mAP50-95(B)'].max()
best_ep_map   = df['metrics/mAP50-95(B)'].idxmax()

print(f"\nMELHORES RESULTADOS:")
print(f"  Melhor mAP50:    {best_mAP50:.4f}  (epoca {best_ep_50})")
print(f"  Melhor mAP50-95: {best_mAP:.4f}  (epoca {best_ep_map})")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

axes[0, 0].plot(df['epoch'], df['train/box_loss'], label='Box Loss', linewidth=2)
axes[0, 0].plot(df['epoch'], df['train/cls_loss'], label='Class Loss', linewidth=2)
axes[0, 0].plot(df['epoch'], df['train/dfl_loss'], label='DFL Loss', linewidth=2)
axes[0, 0].set_title('Loss durante Treinamento')
axes[0, 0].set_xlabel('Epoca')
axes[0, 0].set_ylabel('Loss')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].plot(df['epoch'], df['metrics/precision(B)'], label='Precision', linewidth=2)
axes[0, 1].plot(df['epoch'], df['metrics/recall(B)'],    label='Recall',    linewidth=2)
axes[0, 1].set_title('Precisao e Recall')
axes[0, 1].set_xlabel('Epoca')
axes[0, 1].set_ylabel('Valor')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

axes[0, 2].plot(df['epoch'], df['metrics/mAP50(B)'],    label='mAP50',    linewidth=2)
axes[0, 2].plot(df['epoch'], df['metrics/mAP50-95(B)'], label='mAP50-95', linewidth=2)
axes[0, 2].set_title('mAP (Mean Average Precision)')
axes[0, 2].set_xlabel('Epoca')
axes[0, 2].set_ylabel('mAP')
axes[0, 2].legend()
axes[0, 2].grid(True, alpha=0.3)

lr_col = 'lr/pg0' if 'lr/pg0' in df.columns else 'x/lr0'
axes[1, 0].plot(df['epoch'], df[lr_col], label='Learning Rate', linewidth=2, color='green')
axes[1, 0].set_title('Taxa de Aprendizado')
axes[1, 0].set_xlabel('Epoca')
axes[1, 0].set_ylabel('LR')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].plot(df['epoch'], df['metrics/mAP50(B)'], label='mAP50 geral', linewidth=2, color='red')
axes[1, 1].set_title('Evolucao mAP50')
axes[1, 1].set_xlabel('Epoca')
axes[1, 1].set_ylabel('mAP50')
axes[1, 1].grid(True, alpha=0.3)

ax = axes[1, 2]
ax.axis('off')
texto = (
    f"RESUMO FINAL:\n\n"
    f"Melhor mAP50:    {best_mAP50:.4f}\n"
    f"Melhor mAP50-95: {best_mAP:.4f}\n"
    f"Melhor Precisao: {df['metrics/precision(B)'].max():.4f}\n"
    f"Melhor Recall:   {df['metrics/recall(B)'].max():.4f}\n\n"
    f"Ultima epoca:\n"
    f"  mAP50:    {df['metrics/mAP50(B)'].iloc[-1]:.4f}\n"
    f"  mAP50-95: {df['metrics/mAP50-95(B)'].iloc[-1]:.4f}\n"
    f"  Loss:     {df['train/box_loss'].iloc[-1]:.4f}\n\n"
    f"Melhor epoca: {best_ep_map}"
)
ax.text(0.1, 0.5, texto, transform=ax.transAxes, fontsize=10,
        verticalalignment='center', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
saida = RESULTS_DIR / 'analise_completa.png'
plt.savefig(str(saida), dpi=300)
print(f"\nGrafico salvo em: {saida}")
plt.show()

loss_train = df['train/box_loss'].values
loss_val   = df['val/box_loss'].values

if len(loss_train) > 10:
    ult_train = loss_train[-10:].mean()
    ult_val   = loss_val[-10:].mean()
    print(f"\nANALISE DE OVERFITTING:")
    print(f"  Loss treino (ultimas 10 epocas):    {ult_train:.4f}")
    print(f"  Loss validacao (ultimas 10 epocas): {ult_val:.4f}")
    if ult_val > ult_train * 1.2:
        print("  ⚠️  Possivel overfitting! Considere mais imagens ou mais regularizacao.")
    else:
        print("  ✅ Sem sinais de overfitting")

print("\n" + "=" * 60)
