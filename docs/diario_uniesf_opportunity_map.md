# Diário do projeto — UNIESF Opportunity Map

**Última atualização:** 29/10/2026  
**Regra de registro:** somente etapas efetivamente executadas e resultados confirmados durante o trabalho. Dados e indicadores não representam necessariamente pessoas únicas.

## 1. Organização e inventário dos dados — concluído
- Organização do projeto por dados originais (`data/raw/`), processados (`data/processed/`), notebooks e relatórios.
- Inventário físico e estrutural dos arquivos CSV de migração, trabalho e educação.
- Inspeção de formatos, codificações, colunas e contagens de linhas; tratamento da presença de arquivos temporários do LibreOffice no inventário.

## 2. SISMIGRA: exploração, qualidade e geografia — concluído
- Leitura e exploração dos registros de 2024, 2025 e janeiro–agosto de 2026.
- Harmonização da variável de faixa etária: em 2026, derivada de `IDADE`; registros sem idade válida mantidos na categoria não especificada. Identificados 30.302 valores ausentes e 622 idades negativas em 2026.
- Verificação de campos geográficos e exclusão, nos DataFrames de análise municipal, dos registros sem município identificado. Registros repetidos não foram eliminados automaticamente por não haver identificador individual adequado.
- Construção e salvamento de tabela de referência municipal do IBGE (`data/processed/municipios_ibge.parquet`).
- Padronização de grafias municipais e associação de códigos IBGE de 7 dígitos. Registros de `JUREMA (MT)` permaneceram sem correspondência confirmada: 38 (2024), 18 (2025) e 33 (2026).
- Validação de registros com código IBGE: 222.574 (2024), 236.777 (2025), 153.078 (2026); os respectivos totais foram reconciliados com a tabela consolidada.
- Construção de indicadores municipais: registros anuais de 2024 e 2025, registros parciais de 2026, variação absoluta e percentual de 2024 para 2025. Consolidação de 934 municípios, incluindo 46 encontrados exclusivamente em 2026.
- Exportação em `data/processed/migracao/indicadores_migracao_municipal.parquet`, com códigos IBGE convertidos para inteiro.

## 3. CAGED: movimentações e indicadores territoriais — concluído
- Exploração dos arquivos de movimentações CAGED de 2025 e janeiro–julho de 2026.
- Confirmação da codificação de movimentações: `+1` para admissões e `-1` para desligamentos.
- Associação dos códigos municipais de 6 dígitos do CAGED aos códigos IBGE de 7 dígitos; códigos `999999` não foram incluídos nas análises municipais.
- Em 2025, 709.021 movimentações com município identificado; saldo anual municipal agregado de +77.909.
- Comparação de janeiro–julho de 2025 e 2026 com mesmo critério geográfico: admissões de 231.492 e 275.160; desligamentos de 181.985 e 221.328; saldos de +49.507 e +53.832, respectivamente.
- Construção de tabela comparativa municipal de admissões, desligamentos e saldo nos dois períodos, incluindo variação absoluta e percentual das admissões.
- Validação dos totais de admissões, desligamentos e saldos: diferenças iguais a zero nos dois períodos.
- Exportação em `data/processed/trabalho/indicadores_emprego_2025_2026.parquet`.

## 4. CAGED e CBO: ocupações — indicadores por ocupação validados
- Carregamento de tabela de ocupações CBO e verificação de tipos e unicidade dos códigos.
- Cruzamento dos códigos de ocupação do CAGED 2025 com suas descrições oficiais, usando `merge(..., validate="many_to_one")`.
- Após substituição da tabela CBO por versão mais completa, restaram 202 registros sem descrição, distribuídos em 14 códigos distintos.
- Substituição dos títulos ausentes por `Não identificado` no DataFrame de trabalho.
- Construção do DataFrame `ranking_ocupacoes_2025`, com contagens de admissões por título de ocupação, ordenadas do maior para o menor.
- Construção e execução de `emprego_por_ocupacao_2025` com agrupamento por `TITULO`, contendo admissões, desligamentos e saldo por ocupação.
- Validação dos totais agregados por ocupação: 393.465 admissões, 315.556 desligamentos e saldo +77.909; 709.021 movimentações, em concordância com os indicadores municipais de 2025.

## 5. CAGED e CNAE: análise por seção econômica — concluído (22/10/2026)
- Carregamento da tabela `cnae_secoes.csv`, contendo 21 seções CNAE e suas descrições, e conferência da compatibilidade de tipos e ausência de códigos duplicados.
- Associação das descrições de seção ao CAGED 2025, com 709.021 movimentações preservadas e nenhuma descrição de seção ausente.
- Contagem das admissões por seção e criação de `emprego_por_setor_2025`, com admissões, desligamentos e saldo por `descricao_secao`.
- Ranking dos maiores saldos positivos: indústrias de transformação (+26.803), comércio e reparação de veículos (+19.960), atividades administrativas e serviços complementares (+7.600), alojamento e alimentação (+6.421), construção (+5.419).
- Validação final dos totais por seção CNAE: 393.465 admissões, 315.556 desligamentos, saldo +77.909, exatamente iguais aos totais consolidados do CAGED municipal de 2025.

## 6. CNAE: subclasses e grupos econômicos — concluído (22/10/2026)
- Preparados três arquivos de referência a partir da estrutura detalhada da CNAE 2.3: `cnae_grupos.csv` (285 linhas), `cnae_classes.csv` (673 linhas) e `cnae_subclasses.csv` (1.331 linhas).
- Importação de `data/raw/trabalho/cnae/cnae_subclasses.csv`: 1.331 linhas, 7 colunas e 1.331 códigos únicos em `codigo_numerico`; chave `int64`, sem nulos, compatível com `caged_completo["subclasse"]`.
- Cruzamento `caged_atividades = caged_completo.merge(subclasses_cnae, left_on="subclasse", right_on="codigo_numerico", how="left", validate="many_to_one")`: preservadas 709.021 movimentações do CAGED 2025.
- Identificadas 122 movimentações sem correspondência de subclasse/descrição/grupo, distribuídas entre os códigos `9900800` (119) e `8630505` (3); filtros confirmaram que ambos estão ausentes em `subclasses_cnae`. **Não foram excluídas do DataFrame original de análise**; ficam fora de agregações por grupo feitas com o `groupby` padrão.
- A tabela de subclasses possui 282 grupos únicos; o CAGED associado possui 271 grupos CNAE distintos, com 122 valores ausentes na coluna `grupo`.
- Criado `emprego_por_grupo_2025`, com `groupby("grupo").agg(...)`: admissões (`+1`), desligamentos (`-1`) e saldo por grupo.
- Importada a referência `cnae_grupos.csv`: 285 linhas, 5 colunas, 285 grupos únicos e nenhum grupo duplicado. Identificado que os códigos `grupo` foram lidos como `float64`, o que remove zeros à esquerda na representação (p.ex., `01.1` vira `1.1`).
- Criado `ranking_grupos_2025` com `reset_index()` e `merge()` por grupo com a referência de descrições (`how="left", validate="many_to_one"`). **Validação:** 271 linhas e **zero descrições ausentes**.
- Cinco maiores saldos de emprego por grupo CNAE em 2025: `10.1` Abate e fabricação de produtos de carne (+13.212); `47.1` Comércio varejista não especializado (+9.931); `56.1` Restaurantes e outros serviços de alimentação (+4.355); `41.2` Construção de edifícios (+1.871); `81.2` Atividades de limpeza (+1.800).
- Executado pelo usuário o comando `ranking_grupos_2025.to_parquet(path="../data/processed/trabalho/emprego_por_grupo_2025.parquet")`; a execução não teve erro relatado. O arquivo está no ambiente local do usuário, não neste ambiente do diário.

## 7. CAGED por município e grupo CNAE — concluído (23–27/10/2026)
- Agrupado `caged_atividades` por `codigo_ibge` e `grupo`, com contagem de admissões (`saldomovimentacao == 1`), desligamentos (`== -1`) e soma do saldo.
- Resultado: **29.601 combinações município–grupo** em **1.054 municípios**; `122` movimentações sem grupo ficam fora do agrupamento.
- Adicionadas informações territoriais do IBGE (nome do município e UF) e descrições oficiais dos grupos CNAE. Após limpeza de colunas redundantes: **29.601 linhas**, descrições completas, `codigo_ibge` convertido para `int64`.
- Totais validados: **393.415 admissões, 315.484 desligamentos e saldo +77.931**; diferenças em relação ao CAGED com município identificado correspondem a 50 admissões e 72 desligamentos nos 122 registros sem grupo.
- Executado sem erro relatado o salvamento `data/processed/trabalho/emprego_por_municipio_grupo_2025.parquet` com `index=False`.

## 8. Integração SISMIGRA + CAGED 2025 — concluída (26–27/10/2026)
- Recarregado o arquivo `data/processed/migracao/indicadores_migracao_municipal.parquet`: **934 municípios**, 8 colunas, `codigo_ibge` do tipo `Int64`, sem duplicatas nem nulos.
- Agregados os indicadores de trabalho por município em `emprego_municipal_2025`: **1.054 municípios**, códigos únicos e totais reconciliados (**393.415 admissões, 315.484 desligamentos, saldo +77.931**).
- Feito `outer merge` por `codigo_ibge`, com `validate="one_to_one"` e `indicator=True`: **1.228 municípios** distintos, sendo **760 presentes nas duas fontes**, **174 apenas no SISMIGRA** e **294 apenas no CAGED**.
- Verificado que todos os 1.228 códigos possuem correspondência na referência oficial IBGE. Completados `municipio` e `uf` por `fillna()` a partir da referência; nenhuma identificação geográfica permaneceu ausente. Removidas as colunas geográficas auxiliares, mantendo `_merge` para rastrear cobertura.
- Identificados **481 valores ausentes** em `variacao_%`: **294** correspondem a municípios exclusivos do CAGED, e **187** a municípios presentes no SISMIGRA com **zero registros em 2024**; preservados como nulos por não haver denominador válido.
- Mantidos `NaN` nos indicadores de fonte ausente, sem converter automaticamente em zeros: **294** municípios sem indicadores migratórios no cruzamento e **174** sem indicadores de emprego.
- Validação aritmética: **1.054 municípios verificados**, **zero divergências** na identidade `saldo = admissoes - desligamentos`.
- Usuário confirmou a exportação da base `data/processed/indicadores_integrados_municipais.parquet`, com `_merge` convertido para texto e `index=False`; contém **1.228 municípios** e **12 colunas** na versão salva.

## 9. Exploração integrada e correlações — concluída (27–28/10/2026)
- Explorado ranking municipal por registros SISMIGRA em 2025: São Paulo **38.523**, Boa Vista **35.014**, Curitiba **12.861**, Manaus **8.759**, Rio de Janeiro **7.426** entre os cinco primeiros.
- Explorado ranking de saldo CAGED 2025: Curitiba **+7.422**, São Paulo **+6.489**, Chapecó **+2.416**, Cascavel **+1.939**, Joinville **+1.842** entre os cinco primeiros; também examinados municípios com saldos negativos (menor: Nova Erechim/SC, **−167**).
- Analisadas as distribuições com `.describe()`: SISMIGRA 2025, mediana **34**, máximo **38.523**; admissões, mediana **54**, máximo **34.973**; saldo, mediana **14**, máximo **7.422**. Observada forte assimetria positiva.
- Instalado/acionado Matplotlib para gráficos e produzidos histogramas de registros migratórios e admissões. Aplicada transformação `np.log1p()` para visualizar distribuições sem a distorção causada pela magnitude dos extremos; produzidos gráficos de dispersão nas escalas original e logarítmica.
- Correlações calculadas nos municípios com pares de valores disponíveis (**760 municípios** nas análises migração × emprego): Pearson, SISMIGRA 2025 × admissões nos valores originais **0,737113**; Pearson na escala `log1p` **0,694214**; Spearman SISMIGRA 2025 × admissões **0,699864**; Spearman SISMIGRA 2025 × saldo **0,557984**. Spearman admissões × saldo **0,73616**.
- Interpretação registrada: associação positiva não implica causalidade, os registros SISMIGRA não medem estoque de população migrante, e `saldo` é parcialmente derivado de admissões. Admitidas candidaturas a indicadores principais de migração e admissões, mas **sem definir pesos ou ranking final**.
- Criadas as colunas exploratórias `log_migracao` e `log_admissoes` no DataFrame em memória; a exportação anterior da base integrada ocorreu antes dessas colunas exploratórias.

## 10. Inventário e exploração do Censo Escolar 2025 — concluídos em 29/10/2026
- Confirmada pelo usuário a criação de `notebooks/03_exploracao_educacao.ipynb`.
- Inspecionada `data/raw/educacao/` com `Path.rglob("*.csv")`: **8 arquivos**, sendo seis do Censo Escolar 2025 e dois da educação superior 2024.
- Carregada `Tabela_Curso_Tecnico_2025_V2.csv` em `cursos_tecnicos`: **32.136 registros, 49 colunas**, **12.026 instituições**, **195 códigos distintos de curso**, **3.385 municípios**, nenhuma duplicata na chave instituição–curso. Seis campos essenciais sem ausentes.
- Verificado que `QT_CURSO_TEC = 1` em todas as 32.136 linhas: cada registro representa uma combinação instituição–curso. Matrículas por registro: mínimo 1, mediana 44, média ~77,49, máximo **16.254**.
- Investigado o maior registro: **Instituto Monitor Ltda (São Paulo/SP), Transações Imobiliárias, 16.254 matrículas**, em curso subsequente (`QT_MAT_CURSO_TEC_SUBS`). A instituição soma **13 cursos distintos** e **19.398 matrículas**. Forma subsequente não é sinônimo de EAD.
- Dez maiores registros instituição–curso concentram **2,77775%** das matrículas técnicas dessa tabela; atenção à localização administrativa da instituição em cursos EAD.
- Carregada `Tabela_Turma_2025_V2.csv` em `turmas_2025`: **178.772 registros e 218 colunas**, **178.772 instituições únicas**, sem códigos de instituição repetidos.
- Totais confirmados: **97.865 turmas técnicas** (`QT_TUR_PROF_TEC`) e **6.834 turmas técnicas EAD** (`QT_TUR_PROF_TEC_EAD`) — **6,98% das turmas**; a proporção de turmas não equivale à proporção de matrículas EAD.
- **11.350 instituições** têm ao menos uma turma técnica. Após corrigir uma expressão booleana que usava uma coluna numérica sem `> 0`, a classificação foi validada: **195 exclusivamente EAD**, **476 com oferta mista** e **10.679 exclusivamente não EAD**. Soma = 11.350.
- Confirmado que nenhuma instituição apresenta EAD superior ao total de turmas técnicas nem valor ausente de EAD quando há turmas técnicas. Investigados maiores estabelecimentos EAD (SENAC EAD RS, UNINTER e SENAI Escola Digital, entre outros).
- Para o Instituto Monitor, `QT_TUR_PROF_TEC = 13` e `QT_TUR_PROF_TEC_EAD = 13`, indicando turmas técnicas inteiramente EAD no agregado da instituição. **A tabela de turmas não vincula essas turmas a cada curso específico**, portanto a modalidade de todas as 16.254 matrículas do curso não foi identificada individualmente.

## 11. Indicadores municipais de oferta educacional — concluídos em 29/10/2026
- Comparada cobertura territorial: **3.385 municípios** na tabela de cursos e **3.344** com ao menos uma turma técnica. Confirmados **41 municípios presentes apenas na tabela de cursos** e **zero exclusivos da tabela de turmas técnicas**. Exemplos desses 41 possuem matrículas pequenas, mas não se inferiu que sejam erros nem se descartaram os registros.
- Construído `educacao_municipal_2025`, com `groupby("CO_MUNICIPIO")`: instituições técnicas distintas (por `CO_ENTIDADE`), ofertas instituição–curso (`size`), cursos distintos (`nunique`), matrículas técnicas (`sum`). **3.385 municípios, 5 colunas** antes de incorporar turmas.
- Construído `turmas_municipais_2025`, somando totais de turmas técnicas e EAD por município: **5.571 municípios, 3 colunas**, sem duplicatas; total de **97.865** e **6.834**, respectivamente.
- Associadas as duas tabelas por `CO_MUNICIPIO` com `left merge` e `validate="one_to_one"`: **3.385 municípios, 7 colunas**, sem nulos.
- Criado `percentual_ead` com `np.where()`: `turmas_tecnicas_ead / turmas_tecnicas * 100` quando o denominador é positivo, caso contrário `NaN`. Verificação: **41 não calculáveis**, nenhum valor acima de 100%, média municipal **1,941361%**, mediana e quartil 75% iguais a zero, máximo 100%. Essa média municipal difere da proporção nacional ponderada por turmas (~6,98%).
- Comparados municípios líderes por número absoluto de turmas EAD e por participação percentual (com limite exploratório mínimo de 20 turmas). Porto Alegre: **981 EAD/1.604 totais (61,16%)**; Curitiba: **661/1.644 (40,21%)**; Florianópolis: **230/588 (39,12%)**; São Paulo: **192/5.751 (3,34%)**.
- Associada referência oficial de códigos IBGE, nomes municipais e UFs, sem correspondências ausentes: **3.385 linhas, 11 colunas** antes da remoção de `CO_MUNICIPIO`.
- Usuário confirmou salvamento da tabela municipal em `data/processed/educacao/indicadores_educacao_municipal_2025.parquet`, após instrução para preservar `codigo_ibge` e remover o identificador municipal redundante.

## 12. Oferta técnica por área e por curso — concluída a agregação em 29/10/2026
- Criado `oferta_por_area_2025`: ofertas, cursos distintos, instituições e matrículas por área de formação. Principais áreas por ofertas: **Gestão e negócios (9.609; 711.071 matrículas)**, **Informação e comunicação (5.738; 424.627)** e **Ambiente e saúde (5.668; 503.998)**.
- Criado `oferta_por_curso_2025`: ofertas, municípios atendidos e matrículas por curso. Principais cursos por ofertas: Administração (**4.877 ofertas, 1.947 municípios, 395.059 matrículas**), Enfermagem (**2.245, 955, 298.699**), Informática (**2.052, 1.206, 167.134**), Desenvolvimento de Sistemas (**1.977, 784, 150.862**) e Logística (**1.473, 635, 88.259**).
- Criado `educacao_municipio_curso_2025`, agrupando por município, código e nome de curso e área profissional, com instituições distintas e soma de matrículas: **18.793 combinações município–curso e 6 colunas**, **2.490.145 matrículas agregadas**, correspondendo exatamente às **2.490.145 originais**, **zero combinações duplicadas**.
- Foi fornecido código para renomear `CO_MUNICIPIO` para `codigo_ibge` e salvar `data/processed/educacao/educacao_municipio_curso_2025.parquet`, **mas a execução e a exportação deste arquivo detalhado ainda não foram confirmadas pelo usuário**.
- Convenção de trabalho acordada: reduzir exercícios repetitivos, priorizar conceitos novos e explicar brevemente com comentários `#` todo código fornecido para copiar.

## Pendências (não concluídas)
- **Retomada:** confirmar a execução do salvamento da base detalhada `educacao_municipio_curso_2025.parquet`; depois começar a **correspondência documentada entre cursos técnicos INEP, ocupações CBO e grupos CNAE**, evitando equivalências automáticas ou inferências de demanda.
- Explorar, se pertinente, as bases de escolas e de educação superior 2024 e integrar os indicadores educacionais à base SISMIGRA–CAGED por `codigo_ibge`, respeitando a granularidade.
- Retomar CAGED **2026 (janeiro–julho)** por ocupações e grupos CNAE e comparar ao período equivalente de 2025; a comparação municipal parcial anterior já foi salva.
- Definir critérios e pesos de priorização territorial somente após avaliação metodológica e análise de sensibilidade.
- Verificar os códigos CNAE sem correspondência (`9900800`, `8630505`), com atenção à versão da classificação.
- Padronizar códigos CNAE como texto com zeros à esquerda nas tabelas finais; verificar se tabelas derivadas por CBO e seção CNAE precisam ser persistidas.

---

**Nota metodológica:** os registros SISMIGRA são administrativos e não equivalem necessariamente à população residente ou a indivíduos únicos. O CAGED mede movimentações formais, não vagas abertas ou demanda direta por capacitação. Cursos e matrículas informam oferta/cadastros educacionais e podem refletir instituições EAD com alcance supramunicipal. A presença administrativa da instituição no município não localiza necessariamente cada estudante.
