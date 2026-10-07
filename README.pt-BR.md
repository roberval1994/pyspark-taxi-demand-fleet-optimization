<h1 align="center">🚕 Táxis de NYC — Previsão de Demanda Distribuída & Otimização de Frota</h1>

<p align="center">
  <b>Machine Learning em big data (PySpark) encontra Pesquisa Operacional</b><br>
  Preveja a demanda por zona com Spark MLlib e então <i>decida</i> como alocar a frota com um modelo de otimização exato.
</p>

🌐 **Idioma / Language:** **Português** | [English](README.md)

---

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-3.4%2B-E25A1C.svg?logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Solver](https://img.shields.io/badge/Otimizacao-PuLP%20%2F%20CBC-success.svg)]()
[![Tests](https://img.shields.io/badge/testes-pytest-brightgreen.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 O que este projeto demonstra

Duas competências que raramente aparecem juntas, aplicadas a um problema realista:

1. **Machine Learning em escala** — usando **PySpark / Spark MLlib** para processar milhões
   de corridas de táxi de Nova York e prever a demanda horária por zona.
2. **Pesquisa Operacional** — transformar essa previsão em uma **decisão acionável**: um
   Programa Linear Inteiro (PLI) exato que aloca uma frota limitada entre as zonas para
   maximizar a demanda coberta.

A narrativa é **prever → decidir**: uma previsão só é útil se levar a uma decisão melhor.
Isso espelha o trabalho real de logística (posicionamento de frota, alocação de recursos).

## 🗺️ Visão geral do pipeline

```
 Corridas NYC TLC (Parquet, milhões de linhas)
        │   PySpark: leitura + limpeza
        ▼
 Tabela de demanda zona–hora  ──►  Spark MLlib (regressor GBT)  ──►  previsão por zona
        │                                                               │
        │                                            Pesquisa Operacional (PuLP / CBC)
        ▼                                                               ▼
  atributos de calendário                          alocação exata da frota + baseline
```

## 🗂️ Estrutura do projeto

```
pyspark-taxi-demand-fleet-optimization/
├── data/
│   └── raw/                     # Arquivos Parquet da NYC TLC (não versionados)
├── notebooks/
│   └── 00_walkthrough.ipynb     # Tour guiado e documentado, ponta a ponta
├── src/taxi_pipeline/
│   ├── config.py                # Caminhos, URLs do dataset, parâmetros ajustáveis
│   ├── spark_session.py         # Fábrica da SparkSession
│   ├── ingest.py                # Leitura e limpeza das corridas (Spark)
│   ├── features.py              # Tabela zona-hora + atributos de calendário (Spark)
│   ├── model.py                 # Modelo de demanda Spark MLlib (treino/avaliação)
│   └── optimize.py              # PLI de alocação de frota + baseline guloso (PuLP)
├── scripts/
│   └── run_pipeline.py          # Execução ponta a ponta em um comando
├── tests/
│   └── test_optimize.py         # Testes da otimização (não exigem Spark)
├── requirements.txt
├── LICENSE
├── README.md                    # Inglês
└── README.pt-BR.md              # Português (este arquivo)
```

## 🔬 Etapas do pipeline

| Etapa | Módulo | O que faz |
|---|---|---|
| **1. Ingestão** | `ingest.py` | Lê os Parquet mensais e aplica filtros de qualidade |
| **2. Atributos** | `features.py` | Agrega corridas em tabela zona-hora; adiciona atributos de calendário |
| **3. Modelo** | `model.py` | Treina regressor **GBT** do Spark MLlib; avaliação cronológica (RMSE/MAE/R²) |
| **4. Previsão** | `model.py` | Prevê a demanda por zona para o horizonte de planejamento |
| **5. Otimização** | `optimize.py` | **PLI exato** aloca a frota; comparado a um baseline guloso |

## ⚡ Início rápido

```bash
git clone https://github.com/roberval1994/pyspark-taxi-demand-fleet-optimization.git
cd pyspark-taxi-demand-fleet-optimization

python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Baixe pelo menos um mês de dados em data/raw/ (ver data/README.md) e então:
python scripts/run_pipeline.py
```

> **Requisito do Spark:** o PySpark precisa de um runtime Java (JDK 8/11/17). No Windows, o
> Anaconda facilita isso. O **módulo de otimização e seus testes rodam sem o Spark**.

## 🧪 Testes

```bash
pytest -q
```

A otimização é coberta por testes unitários — incluindo a verificação de que o **PLI exato
nunca é pior que a heurística gulosa**, e de que as restrições de orçamento de frota e de
capacidade por zona são respeitadas.

## 📈 Resultado de exemplo

Em um perfil de demanda de exemplo, com uma frota de 40 veículos, o **PLI exato cobriu ~69%**
da demanda prevista contra **~64%** da regra gulosa proporcional — o tipo de margem que faz
diferença na escala de uma cidade.

## 🧰 Tecnologias

`PySpark` · `Spark MLlib` · `PuLP` (CBC) · `pandas` · `NumPy` · `Matplotlib` · `pytest`

## 📚 Princípios de design

- **Degrada com elegância**: os imports do Spark são lazy, então o pacote importa e os
  testes de PO rodam mesmo sem o Spark instalado.
- **Sem vazamento temporal**: o modelo de demanda é avaliado em um conjunto cronológico.
- **A previsão alimenta a decisão**: a saída do ML é a entrada do otimizador — uma história
  coerente.
- **Exato vs. heurística**: o PLI é comparado a um baseline, como no trabalho real de PO.

## 👤 Autor

**Roberval Gonçalves Moreira Filho** — Cientista de Dados | Analista de Pesquisa Operacional

[![LinkedIn](https://img.shields.io/badge/LinkedIn-robervalOr-blue)](https://www.linkedin.com/in/robervalOr)
[![Lattes](https://img.shields.io/badge/Lattes-CNPq-00599C)](http://lattes.cnpq.br/4394523940603239)
[![GitHub](https://img.shields.io/badge/GitHub-roberval1994-black)](https://github.com/roberval1994)

## 📄 Licença

Distribuído sob a Licença MIT. Veja [LICENSE](LICENSE).
