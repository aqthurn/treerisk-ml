# Tree Risk AI — Manual de Uso

Detecção de sinais de risco em árvores urbanas (visão computacional, YOLOv8).
Este manual explica como **rodar o pipeline** (preparar dados, treinar, testar)
usando Docker, e **onde colocar as imagens e labels**.

---

## 1. Pré-requisitos

- **Docker Desktop** instalado e **rodando** (o ícone da baleia precisa estar ativo
  na bandeja). Em Windows, precisa de WSL2 habilitado.
- A pasta do projeto (`treerisk-ml/`) na sua máquina.

> Você **não precisa** instalar Python, YOLO ou nada disso. Tudo já está dentro da
> imagem Docker. Só o Docker Desktop é necessário.

---

## 2. Estrutura de pastas (IMPORTANTE)

Todos os comandos são rodados **de dentro da pasta `treerisk-ml/`**. A estrutura é:

```
treerisk-ml/                  ← rode os comandos AQUI
├── dockerfile
├── config.py
├── requirements.txt
├── configs/
│   └── data.yaml             ← lista de classes (NÃO edite sem necessidade)
├── scripts/                  ← os scripts do pipeline
├── dataset/                  ← OS DADOS (imagens e labels)
│   ├── images/
│   │   ├── all/              ← TODAS as imagens vão AQUI
│   │   ├── treino/           ← gerado automaticamente (não mexer)
│   │   ├── validacao/        ← gerado automaticamente (não mexer)
│   │   └── teste/            ← gerado automaticamente (não mexer)
│   └── labels/
│       ├── all/              ← TODOS os labels (.txt) vão AQUI
│       ├── treino/           ← gerado automaticamente (não mexer)
│       ├── validacao/        ← gerado automaticamente (não mexer)
│       └── teste/            ← gerado automaticamente (não mexer)
├── modelos/                  ← onde o modelo treinado (.pt) é salvo
└── resultados/               ← onde ficam gráficos e métricas do treino
```

**Regra de ouro:** você só coloca arquivos em `dataset/images/all/` e
`dataset/labels/all/`. As pastas `treino/`, `validacao/` e `teste/` são
**geradas pelo script** — nunca coloque nada nelas na mão.

---

## 3. Onde e como colocar imagens e labels

### Imagens → `dataset/images/all/`
- Formato: **`.jpg`** (preferencial), `.jpeg` ou `.png`.
- **HEIC (iPhone) NÃO funciona direto** — precisa ser convertido para `.jpg` antes.
- Nome no padrão sequencial: `img_0001.jpg`, `img_0002.jpg`, … Continue a numeração
  a partir do último número que já existe (não repita nem reinicie).

### Labels → `dataset/labels/all/`
- Um arquivo **`.txt`** por imagem, com **o mesmo nome** da imagem.
  Ex: `img_0060.jpg` → `img_0060.txt`.
- Formato **YOLO**, uma linha por caixa:
  ```
  <classe> <x_centro> <y_centro> <largura> <altura>
  ```
  Todos os valores de 0 a 1 (normalizados). Exemplo:
  ```
  0 0.514609 0.708705 0.158398 0.155010
  ```
- Imagem sem defeito pode ter um `.txt` vazio (vira "imagem de fundo").

### ⚠️ ORDEM DAS CLASSES — o erro que corrompe o dataset em silêncio
Ao anotar (ex: no makesense.ai), a ordem das classes **TEM** que ser exatamente:

| índice | classe |
|---|---|
| 0 | cavidade |
| 1 | levantamento_pavimento |
| 2 | poda |
| 3 | raiz_exposta |

Se você anotar com a ordem trocada, os números saem errados e o modelo aprende
associação errada — **sem dar nenhum aviso**. Confira essa ordem antes de cada
sessão de anotação.

### Nome de imagem e label têm que casar
Toda imagem precisa do seu `.txt` de mesmo nome, e vice-versa. Imagem sem label é
ignorada; label sem imagem dá erro.

---

## 4. Baixar a imagem Docker (só na primeira vez)

```powershell
docker pull aqthurn/treerisk-ml:1.0
```

Isso baixa o ambiente pronto (Python + YOLO + scripts). Não precisa buildar nada.

---

## 5. Rodar o pipeline (na ordem)

> **Rode sempre de dentro da pasta `treerisk-ml/`** (a que contém `dataset/`).
> Confira com: `Test-Path .\dataset\images\all` — deve retornar `True`.

> **NÃO use o botão de "play" do Docker Desktop.** Ele roda o container **sem** o
> dataset e você verá `0 imagens`. O dataset precisa ser "montado" com `-v` (volume),
> e isso só é possível pela linha de comando abaixo.

### Passo 1 — Preparar os dados (dividir em treino/validação/teste)

```powershell
docker run --rm `
  -v ${PWD}\dataset:/app/dataset `
  aqthurn/treerisk-ml:1.0 python scripts/preparar_dados.py
```

Ele imprime a distribuição por classe. Confira que **nenhuma classe fica com 0 no
treino**. Rode este passo sempre que adicionar imagens/labels novos.

### Passo 2 — Treinar

```powershell
docker run --rm `
  -v ${PWD}\dataset:/app/dataset `
  -v ${PWD}\modelos:/app/modelos `
  -v ${PWD}\resultados:/app/resultados `
  aqthurn/treerisk-ml:1.0 python scripts/treinar_otimizado.py
```

O modelo treinado (`.pt`) aparece em `modelos/` e os gráficos/métricas em
`resultados/`. Em CPU o treino é **lento** (pode levar horas dependendo do número
de épocas).

### Passo 3 — Testar o modelo numa imagem

```powershell
docker run --rm `
  -v ${PWD}\dataset:/app/dataset `
  -v ${PWD}\modelos:/app/modelos `
  -v ${PWD}\resultados:/app/resultados `
  aqthurn/treerisk-ml:1.0 python scripts/testar_imagem.py
```

---

## 6. Sobre os volumes (`-v`) — por que são obrigatórios

A imagem Docker contém **só o código e o ambiente** — de propósito, **não** contém
o dataset. Por isso todo comando que usa dados precisa dos `-v`:

- `-v ${PWD}\dataset:/app/dataset` → deixa o container **ler** suas imagens/labels.
- `-v ${PWD}\modelos:/app/modelos` → salva o modelo treinado na sua máquina.
- `-v ${PWD}\resultados:/app/resultados` → salva gráficos e métricas na sua máquina.

**Sem os `-v`, o container não enxerga nada e o que ele gerar é perdido** quando ele
termina. No Linux/Mac, troque `${PWD}\dataset` por `$(pwd)/dataset`.

---

## 7. Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `0 imagens` / `NENHUMA IMAGEM ENCONTRADA` | Rodou sem `-v` (ou pelo botão play) | Use o comando com `-v ${PWD}\dataset:/app/dataset` |
| `error during connect ... docker daemon` | Docker Desktop não está rodando | Abra o Docker Desktop e espere a baleia ficar ativa |
| Caminho de dataset vazio | Rodou da pasta errada | `cd` para `treerisk-ml/`; confira com `Test-Path .\dataset` |
| Label sem efeito / classe errada | Ordem de classes trocada na anotação | Reanote com a ordem da seção 3 (0=cavidade...) |
| Imagem HEIC não carrega | HEIC não é suportado | Converta para `.jpg` antes de colocar em `all/` |
| Modelo não encontrado no teste | Nome do `.pt` diferente do esperado | Aponte o script para o `.pt` real em `modelos/` |

---

## 8. Fluxo resumido para adicionar dados novos

1. Converta as fotos para `.jpg` e renomeie continuando a numeração (`img_00NN.jpg`).
2. Anote (respeitando a **ordem das classes** da seção 3) e gere os `.txt`.
3. Copie as imagens para `dataset/images/all/` e os labels para `dataset/labels/all/`.
4. Rode o **Passo 1** (`preparar_dados.py`) para re-dividir os splits.
5. Rode o **Passo 2** (`treinar_otimizado.py`) para treinar.

---

## 9. Classes do modelo (referência)

| índice | classe | descrição |
|---|---|---|
| 0 | cavidade | oco, buraco ou cavidade no tronco |
| 1 | levantamento_pavimento | calçada levantada/rachada por raiz |
| 2 | poda | marcas/necessidade de poda |
| 3 | raiz_exposta | raízes expostas ou superficiais |
