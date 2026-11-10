# SISMIGRA: série 2022–2026, países e cadastro ativo

Análise executada em 10/11/2026 com os arquivos locais de `data/raw/migracao/`. Essa é a data do processamento, **não a data de referência do cadastro ativo**, que não consta na extração.

## Resultados dos arquivos anuais

| Ano | Registros no arquivo | Com código IBGE municipal | Sem código IBGE |
| --- | ---: | ---: | ---: |
| 2022 | 243.675 | 220.716 | 22.959 |
| 2023 | 232.193 | 208.376 | 23.817 |
| 2024 | 248.167 | 222.574 | 25.593 |
| 2025 | 265.523 | 236.777 | 28.746 |
| 2026 — janeiro a agosto | 176.896 | 153.078 | 23.818 |

Em 2023, o número de registros foi 4,71% menor que em 2022. Os maiores volumes municipais de 2022 foram Boa Vista/RR (43.132), São Paulo/SP (32.076), Manaus/AM (23.974), Pacaraima/RR (17.392) e Curitiba/PR (6.479). Em 2023, Boa Vista (35.982), São Paulo (31.700) e Manaus (16.743) permaneceram nas três primeiras posições; Curitiba (7.435) e Pacaraima (6.767) completaram as cinco primeiras.

País de origem, na série anual, foi definido operacionalmente como **país de nascimento**. Nacionalidade é outra variável e foi analisada separadamente.

| País de nascimento | Registros 2022 | Participação 2022 | Registros 2023 | Participação 2023 | Registros 2025 | Participação 2025 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Venezuela | 144.755 | 59,40% | 125.759 | 54,16% | 101.652 | 38,28% |
| Bolívia | 15.102 | 6,20% | 16.128 | 6,95% | 21.365 | 8,05% |
| Colômbia | 8.532 | 3,50% | 9.820 | 4,23% | 11.549 | 4,35% |
| Argentina | 7.264 | 2,98% | 8.884 | 3,83% | 13.473 | 5,07% |
| Cuba | 7.130 | 2,93% | 7.717 | 3,32% | 37.451 | 14,10% |

Os arquivos exportados contêm todos os países e anos. A Venezuela lidera nos cinco arquivos anuais, mas perde participação entre 2022 e 2025. Cuba passa de 7.717 registros em 2023 para 16.910 em 2024 e 37.451 em 2025. Essas mudanças na composição dos registros não demonstram, por si, alteração equivalente do estoque de residentes nem suas causas.

Os dados parciais de 2026 têm indicadores de participação, mas não recebem crescimento percentual contra o ano completo de 2025. Os arquivos disponíveis não permitem reconstruir o recorte janeiro–agosto dos anos anteriores, pois `DATAREGISTRO` informa somente o ano.

## Limpeza e cobertura

Os cinco arquivos somam **1.166.454 registros**; **1.041.521** têm município associado à referência local do IBGE. As análises nacionais conservam todas as linhas. As municipais usam apenas linhas com código confirmado, e as estaduais conservam UF inválida/ausente na categoria `NI`.

Foram tratados espaços e caixa, marcadores de ausência, grafias de países, faixas etárias e ano de entrada. Em 2026, as 622 idades negativas permanecem nos totais, sem faixa etária válida. As faixas de 2022–2025 são aquelas divulgadas pelos arquivos; não há idade exata para compará-las à idade de 2026.

As correções municipais mantêm a combinação município–UF, reutilizando as correspondências explícitas anteriores e a referência local. Apóstrofos tipográficos foram harmonizados, Moji Mirim/SP foi associado a Mogi Mirim/SP e São Luiz/RR manteve a correspondência anterior com o código 1400605. Em 2023, Jurema/MT (16 linhas) e Castelo dos Sonhos/PA (10 linhas) permanecem sem atribuição municipal; registros sem município também permanecem sem código. Não houve associação aproximada por semelhança textual.

As grafias originais de país e município são preservadas nas bases completas. O dicionário de equivalências de países harmoniza, por exemplo, INDIA/ÍNDIA e HOLANDA/PAÍSES BAIXOS. Não funde Congo com República Democrática do Congo, nem União Soviética com Rússia. Categorias históricas, territórios, apatridia e nacionalidade indefinida continuam identificáveis. As chaves textuais de país são internas ao projeto, **não códigos ISO**.

Linhas idênticas não foram removidas: os arquivos não têm identificador pessoal e a repetição das características divulgadas não comprova duplicação de pessoas. Os relatórios anuais mostram a contagem de linhas literalmente idênticas; no cadastro por lotes, a auditoria mostra repetições das dimensões agregadas, que também não comprovam duplicidade pessoal.

## Cadastro do arquivo “ativos”

O arquivo tem **3.879.289 registros**, distribuídos assim:

| Situação padronizada | Registros |
| --- | ---: |
| ATIVO | 2.080.214 |
| PRAZO VENCIDO | 1.230.125 |
| CANCELADO | 500.062 |
| INATIVO | 63.671 |
| EXCLUÍDO | 5.217 |

Somente **53,62%** das linhas estão na situação ATIVO. O filtro é aplicado explicitamente; todas as situações são preservadas na base tratada e na tabela por situação.

No recorte ativo, os principais valores da coluna `pais` são Venezuela (643.151; 30,92%), Bolívia (176.955; 8,51%), Portugal (149.004; 7,16%), Haiti (129.121; 6,21%) e Argentina (111.183; 5,34%). As UFs com mais registros ativos são SP (683.487), PR (222.308), SC (219.076), RJ (169.713) e RR (164.432).

A coluna `pais` dessa extração não tem definição fornecida no projeto que permita chamá-la de nascimento ou nacionalidade. Foi mantida como **país informado pela fonte**. Não há município, identificador pessoal ou data de referência. Por isso, o cadastro não é distribuído artificialmente entre municípios, não é transformado em série histórica e não é somado aos registros anuais. A situação ativa é cadastral; não comprova residência atual ou presença física no Brasil.

## Notebooks e execução

As regras compartilhadas estão em `src/migracao.py`, evitando duplicar limpeza nos notebooks.

1. `01_exploracao_migracao.ipynb`: processa 2022–2026; audita ausências, repetições e cobertura; compara municípios; analisa nascimento, nacionalidade, idade, sexo, classificação e situação; exporta bases completas, territoriais, fatos e relatórios de qualidade.
2. `08_exploracao_sismigra_ativos.ipynb`: trata o cadastro por lotes; analisa todas as situações e o recorte ativo, país, UF, sexo, classificação e amparo; exporta as tabelas tratadas.
3. `07_preparacao_powerbi.ipynb`: atualiza as colunas migratórias da base municipal, inclusive 2022/2023, e exporta os fatos e dimensões para o Power BI. Para o restante desse notebook, os indicadores de trabalho e educação já existentes continuam necessários.

Execute os notebooks com o ambiente `.venv`, a partir de `notebooks/`, nessa ordem. Os notebooks 01 e 08 também localizam o projeto quando iniciados na raiz. Os três foram executados e estão salvos com tabelas e gráficos; tabelas longas podem ter a exibição limitada, mas as exportações contêm todas as linhas.

O tratamento requer a referência local `data/processed/municipios_ibge.parquet`, já existente no projeto. Os rankings exploratórios de oportunidade de 2025 não foram recalculados nesta ampliação; as séries históricas e as tabelas de migração foram atualizadas.

## Arquivos para o Power BI

As tabelas abaixo estão em `data/processed/powerbi/`, em **CSV com separador `;` e UTF-8-SIG**, e em **Parquet**. Os CSVs usam ponto decimal; configure o tipo/localidade ao importar percentuais em uma instalação que espere vírgula decimal.

| Tabela fato | Uma linha por | Uso |
| --- | --- | --- |
| `fato_migracao_pais_ano` | Ano × país de nascimento | Totais nacionais, participação e evolução por origem |
| `fato_migracao_nacionalidade_ano` | Ano × nacionalidade | Análise alternativa por nacionalidade |
| `fato_migracao_uf_pais_ano` | Ano × UF × país de nascimento | Análise estadual, incluindo `NI` |
| `fato_migracao_municipio_pais_ano` | Ano × município IBGE × país de nascimento | Mapas e composição municipal |
| `fato_migracao_municipio_ano` | Ano × município IBGE | Evolução dos totais municipais |
| `fato_migracao_perfil_ano` | Ano × país de nascimento × sexo × faixa etária × situação × classificação | Perfil dos registros anuais |
| `fato_sismigra_situacao` | Extração × UF × país da fonte × sexo × situação × classificação × tipologia × amparo | Cadastro completo e filtros cadastrais |
| `fato_sismigra_ativos_uf_pais` | Extração × UF × país da fonte | Recorte ativo estadual |
| `fato_sismigra_ativos_pais` | Extração × país da fonte | Recorte ativo nacional |

As dimensões novas são `dim_paises`, `dim_periodos_migracao` e `dim_ufs`. A `dim_municipios` já existente continua atendendo às tabelas municipais. `dim_periodos_migracao` explicita que 2026 termina em agosto. `snapshot_id` identifica o cadastro disponível sem atribuir uma data desconhecida.

Use relacionamentos 1:N, das dimensões para os fatos, com filtro em um sentido. Relacione `dim_paises[pais_id]` a `pais_origem_id`, `pais_nacionalidade_id` ou `pais_id`, conforme a tabela; ano somente aos fatos anuais; UF aos fatos estaduais e de cadastro; município somente aos fatos municipais.

As nove tabelas são visões dos mesmos universos em níveis diferentes. **Não some fatos nacionais, estaduais, municipais e de perfil, nem faça junção física entre eles.** Para totais nacionais anuais, use `fato_migracao_pais_ano`, que conserva registros sem município; somar os fatos municipais dá apenas o universo territorial identificado.

Os percentuais exportados têm os denominadores documentados nos notebooks e não devem ser somados. Para percentuais que respondem aos filtros do relatório, crie razões de somas. Exemplos de medidas DAX:

```dax
Registros Anuais = SUM(fato_migracao_pais_ano[registros])

Participação Origem =
DIVIDE(
    [Registros Anuais],
    CALCULATE([Registros Anuais], REMOVEFILTERS(dim_paises))
)

Registros Ativos =
CALCULATE(
    SUM(fato_sismigra_situacao[registros]),
    fato_sismigra_situacao[situacao] = "ATIVO"
)
```

A participação acima conserva o filtro de ano e retira o filtro da dimensão de país. Use os campos das dimensões nos segmentadores. Formate a medida como percentual; o resultado de `DIVIDE` é uma fração, enquanto `participacao_pct` nos arquivos está na escala 0–100. Dependendo da configuração regional do Power BI, os argumentos DAX podem exigir ponto e vírgula.

## Verificações realizadas

Os seis testes em `tests/test_migracao.py` passaram, incluindo UF como parte da chave territorial, apóstrofos, idade negativa, ano inconsistente, separação nascimento/nacionalidade e preservação de linhas iguais em lotes distintos do cadastro. Execute-os com:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os notebooks 01, 08 e 07 foram executados integralmente com as gravações reais autorizadas. Totais nacionais, municipais, situações e recorte ativo foram reconciliados. As contagens e variações municipais de 2024–2026 foram comparadas, município a município, com a base anterior: os valores foram preservados. A série ampliada contém 1.015 municípios, contra 934 anteriormente; os municípios adicionais só têm registros identificados em 2022/2023.

Os dados originais e o inventário anteriormente alterado pelo usuário não foram modificados. Os arquivos processados e as exportações são locais e continuam abrangidos pelas regras de exclusão de `data/processed/` no Git. Nenhum relatório foi importado ou modelado dentro do Power BI Desktop nesta etapa.
