# Data / Dados

This project uses the **NYC TLC Trip Records** (yellow taxi), published as monthly
Parquet files. They are **large** and **not versioned** here.

Este projeto usa os **NYC TLC Trip Records** (táxi amarelo), publicados em arquivos
Parquet mensais. Eles são **grandes** e **não são versionados** aqui.

## How to get one month / Como obter um mês

Download any monthly file from the official TLC page and drop it into `data/raw/`:

Baixe qualquer arquivo mensal da página oficial da TLC e coloque em `data/raw/`:

- Official page / Página oficial: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- Direct example / Exemplo direto:
  `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet`

```
data/
└── raw/
    └── yellow_tripdata_2023-01.parquet   # one or more monthly files
```

The pipeline reads **all** Parquet files found in `data/raw/`, so you can add several
months to work at larger scale.

O pipeline lê **todos** os arquivos Parquet em `data/raw/`, então você pode adicionar
vários meses para trabalhar em maior escala.

## Why not versioned? / Por que não versionar?

A single month already has millions of rows (hundreds of MB), well beyond what belongs in
a Git repository. Keeping the data out of Git is standard practice for big-data projects.

Um único mês já tem milhões de linhas (centenas de MB), muito além do que cabe em um
repositório Git. Manter os dados fora do Git é prática padrão em projetos de big data.
