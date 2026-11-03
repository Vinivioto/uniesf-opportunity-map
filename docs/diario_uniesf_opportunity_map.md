# Diário do projeto — UNIESF Opportunity Map

**Última atualização:** 03/11/2026  
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
- Foi fornecido código para renomear `CO_MUNICIPIO` para `codigo_ibge` e salvar `data/processed/educacao/educacao_municipio_curso_2025.parquet`, **e o usuário confirmou posteriormente que o arquivo detalhado foi salvo (ver seção 13)**.
- Convenção de trabalho acordada: reduzir exercícios repetitivos, priorizar conceitos novos e explicar brevemente com comentários `#` todo código fornecido para copiar.

## 13. Retomada da oferta técnica e CBO — 30/10/2026
- Usuário confirmou a existência de `data/processed/educacao/educacao_municipio_curso_2025.parquet` no disco local.
- Revisitado o CAGED 2025, identificando que `caged_atividades` já tinha `cbo2002ocupacao`, `TITULO`, `grupo` e descrições CNAE. Evitou-se novo `merge` de títulos CBO.
- Criado/mostrado ranking `ranking_cbo_2025` agrupado por código CBO e título. Destaques por admissões: alimentador de linha de produção (52.750), faxineiro (26.620), auxiliar nos serviços de alimentação (17.550), magarefe (17.010), servente de obras (15.787), repositor de mercadorias (14.440).
- Proposta uma taxonomia inicial manual de ocupações CBO por trilhas profissionais (produção, comércio, alimentação, logística, construção, limpeza e agropecuária), **sem confirmação de execução, validação ou persistência**. Não tratar como matriz definitiva de cursos.

## 14. Ensino superior 2024 — exploração e base municipal validadas (30/10/2026)
- No `03_exploracao_educacao.ipynb`, carregados `MICRODADOS_CADASTRO_CURSOS_2024.CSV` (**720.349 linhas, 223 colunas**) e `MICRODADOS_ED_SUP_IES_2024.CSV` (**2.561 linhas, 84 colunas**).
- Identificados 2.561 códigos de IES, 46.150 códigos de curso, 3.551 municípios no cadastro de cursos e 698 municípios de sede de IES; 452 repetições de combinação curso–município. `QT_CURSO` = 1 em 45.776 registros e 0 em 674.573 — contar linhas superestimaria a oferta de cursos.
- Estrutura por `TP_DIMENSAO`: presencial municipal (dim. 1, 34.824 linhas, 34.479 cursos contabilizados, 1.121 municípios); EAD territorial (dim. 2, 673.756 linhas, 0 cursos contabilizados, 3.524 municípios); EAD nacional (dim. 3, 11.319 linhas, 11.297 cursos contabilizados, sem município); EAD exterior (dim. 4, 450 linhas).
- Somatórios de matrículas: presencial dimensão 1 **5.037.875**; EAD territorial dimensão 2 **5.186.852** antes de filtrar municípios. Identificados **9 registros EAD sem `CO_MUNICIPIO`**, dos quais dois somam **41 matrículas** (17 + 24). Portanto, **5.186.811 matrículas EAD** foram atribuíveis a municípios. Não imputar localidades desconhecidas.
- Por nacionalidade estrangeira, dimensão 1 **15.981 matrículas** e dimensão 2 **6.939**; isso não identifica refugiados, nem necessariamente pessoas distintas.
- Construídos `presencial_municipal_2024` (cursos presenciais, IES, matrículas, matrículas de estrangeiros) e `ead_municipal_2024` (matrículas EAD, ingressantes EAD e matrículas de estrangeiros EAD).
- Integração `outer` das modalidades em `educacao_superior_municipal_2024`: **3.551 municípios**, 1.094 nas duas modalidades, 27 somente presencial, 2.430 somente EAD; zero duplicações. Após referência IBGE, **3.551 linhas, 10 colunas**, sem nome/UF ausentes.
- **Salvo e confirmado:** `data/processed/educacao/indicadores_ensino_superior_municipal_2024.parquet`.
- Ressalva: dimensão 2 descreve a localização territorial vinculada a polos EAD, **não prova oferta de cursos sediados no município nem residência dos alunos**; dimensão 3 não tem identificação municipal. Presencial 2024 e técnico 2025 não compartilham o mesmo ano-base.

## 15. Base municipal consolidada em quatro dimensões — 30/10/2026
- Criado `04_integracao_indicadores.ipynb`. União `outer` de migração + emprego (**1.228 municípios**) com educação técnica (**3.385**) resultou em **3.689 municípios**: 924 em ambas as bases, 2.461 somente educação técnica e 304 somente na base anterior.
- Corrigidos nomes e UFs com referência IBGE: zero geometadados ausentes e zero códigos duplicados. Cobertura das três dimensões: **2.628 municípios com uma**, **438 com duas** e **623 com três**.
- Inclusão de ensino superior municipal (**3.551**) por `outer merge`: **4.441 municípios** (2.799 ambas as bases, 890 somente anterior, 752 somente superior). Corrigidos 752 nomes/UF ausentes por referência IBGE, sem duplicação.
- Recalculada cobertura: 1 dimensão = 1.536 municípios; 2 = 1.919; 3 = 394; 4 = 592. Individualmente: migração 934, emprego de migrantes 1.054, técnico 3.385, superior 3.551.
- Totais reconciliados na base consolidada: SISMIGRA 2025 **236.777 registros**; CAGED migrantes 2025 **393.415 admissões** (origem município–grupo CNAE, com 50 admissões e 72 desligamentos sem grupo fora do agregado); educação técnica 2025 **2.490.145 matrículas**; superior presencial 2024 **5.037.875 matrículas**; superior EAD territorial 2024 **5.186.811**.
- **Salvo e confirmado:** `data/processed/indicadores_completos_municipais.parquet`, **4.441 linhas, 30 colunas** na versão exportada. Integrações e indicadores posteriores no notebook não estão automaticamente persistidos nesse arquivo anterior.

## 16. Ranking exploratório de volume — 30/10 a 02/11/2026
- Definido universo analítico principal de **760 municípios** com indicadores de migração SISMIGRA 2025 e admissões de migrantes CAGED 2025 simultaneamente.
- Distribuições fortemente assimétricas (SISMIGRA mediana 46,5, máximo 38.523; admissões mediana 90, máximo 34.973). Criados `score_migracao` e `score_emprego` por `np.log1p` e Min-Max dentro dos 760 municípios; ambos no intervalo 0–1.
- Construídos cenários de pesos: equilibrado 50/50, prioridade migração 60/40, prioridade emprego 40/60. Calculadas pontuações e posições. Ranking equilibrado inicial: São Paulo 100,00 (1º), Curitiba 94,77 (2º), Boa Vista 92,17 (3º), Chapecó 84,93 (4º), Manaus 84,22 (5º), Florianópolis 83,23 (6º), Joinville 83,05 (7º), Cascavel 82,62 (8º), Caxias do Sul 81,53 (9º), Rio de Janeiro 81,30 (10º).
- Sensibilidade do ranking: Spearman entre os cenários extremos **0,986**, mudança mediana de 14 posições, mudança média de 23,97, máximo 214; **18 municípios comuns aos três Top 20**. Maiores divergências incluem Pinto Bandeira/RS (0 SISMIGRA, 586 admissões) e Francisco Alves/PR (329 SISMIGRA, 9 admissões).
- Diferença dos componentes normalizados também investigada; isso permite identificar perfis relativos ao próprio índice, não empregabilidade.
- Índice `indice_oportunidade` = 100 × média dos dois scores; exploratório, **não representa população migrante nem potencial de expansão comprovado**. O ranking favorece volume mesmo após a transformação logarítmica.

## 17. Novo Caged geral 2025 — 12 arquivos mensais processados (02/11/2026)
- Usuário baixou os 12 arquivos `CAGEDMOV202501.txt` a `CAGEDMOV202512.txt` em `data/raw/trabalho/caged_geral/`. Criado fluxo no `05_caged_geral.ipynb` com `pd.read_csv(..., chunksize=200_000)`, lendo `uf`, `município`, `saldomovimentação`, `cbo2002ocupação`, `seção`, `subclasse`; contagem de admissões e desligamentos.
- Agregadas três granularidades: município, município × CBO, município × seção e subclasse CNAE. Totais brutos de MOV: **26.321.557 admissões**, **25.064.560 desligamentos**, saldo **+1.256.997**; reconciliados entre as três tabelas.
- Associação do município CAGED de seis dígitos ao código IBGE de sete, com referência previamente validada. Único código não geográfico: `999999` (UF 99), **3.272 admissões e 2.978 desligamentos**, retirado dos agregados municipais, mas reconhecido na reconciliação nacional.
- Tabelas finais, todas sem códigos IBGE ausentes: município **5.566 linhas**; município × CBO **994.623**; município × CNAE **588.508**. Totais idênticos nas três: **26.318.285 admissões**, **25.061.582 desligamentos**, saldo **+1.256.703**.
- **Salvos e confirmados:** `data/processed/trabalho/emprego_geral_municipal_2025.parquet`, `emprego_geral_municipio_cbo_2025.parquet`, `emprego_geral_municipio_cnae_2025.parquet`.
- **Ressalva crucial:** somente `CAGEDMOV` foi processado; arquivos `FOR` e `EXC`, revisões e diferenças de extração não foram reconciliados. Estes totais não devem ser descritos como estatística oficial definitiva de 2025 sem conferência adicional. Uma tabela municipal geral com 5.566 localidades não significa que todos os 5.571 municípios tenham movimentações.

## 18. Integração do mercado geral e indicador de participação migrante (02/11/2026)
- Integração `outer` do emprego geral municipal à base consolidada: **5.567 municípios, 34 colunas**, zero duplicações: 4.440 em ambas as bases, 1.126 somente CAGED geral e 1 somente na base anterior.
- **1.054 municípios** com admissões migrantes e admissões gerais comparáveis; nenhum município apresentou admissões migrantes superiores às gerais.
- Calculada `participacao_migrante_pct` = admissões de migrantes / admissões gerais × 100, com denominador positivo. **0 ausentes e 0 acima de 100%**. Distribuição entre 1.054 municípios: média simples **3,876746%**, mediana **1,348145%**, P95 **15,286325%**, máximo **54,826255%**.
- Maiores percentuais com pelo menos 100 admissões gerais: Pacaraima/RR **54,83%** (142/259), Guatambu/SC **52,77%** (1.826/3.460), Chuí/RS **52,38%** (782/1.493), Pinto Bandeira/RS **51,22%** (586/1.144).
- Participação ponderada apenas entre os 1.054 municípios comparados: **393.415 / 22.215.954 = 1,77%**; média simples dos municípios **3,88%**. **Não chamar 1,77% de participação nacional**, pois o denominador abrange só o subconjunto com registro de migrantes nesta base.
- Comparabilidade ainda precisa ser validada entre a extração de migrantes (CAGED com recorte por país, agregação CNAE com perdas) e CAGED geral MOV; a verificação de percentuais ≤100% é necessária, mas insuficiente.

## 19. População municipal e índice de intensidade — 02/11/2026
- Usuário baixou planilha IBGE com abas `BRASIL E UFS` e `MUNICÍPIOS`, identificada como **estimativas de população residente com referência em 1º de julho de 2026**.
- Leitura da segunda aba com `header=1`, exclusão de coluna vazia, códigos municipais de cinco dígitos preservados como texto; combinação de `COD. UF` (2 dígitos) + `COD. MUNIC` (5) gerou `codigo_ibge` de 7 dígitos. Validada tabela `populacao_municipal`: **5.571 municípios**, sem duplicações e sem população ausente.
- População de 2026 integrada à base de 5.567 municípios, sem ausências. Criado indicador `registros_por_10mil_hab` = SISMIGRA 2025 / população estimada 2026 × 10.000. Cobertura **934 municípios com registros na tabela SISMIGRA**; média 24,501, mediana 8,165, P95 88,141, máximo 898,807.
- Municípios em destaque no indicador: Pacaraima/RR **898,81**, Boa Vista/RR **698,93**, Chuí/RS **425,96**, Barra do Quaraí/RS **400,92**, Bonfim/RR **398,19** registros por 10 mil habitantes.
- Combinados `indice_oportunidade`, `registros_por_10mil_hab` e `participacao_migrante_pct` nos mesmos **760 municípios** do ranking de volume: Spearman volume × registros/hab **0,563674**; volume × participação nas admissões **0,347025**; registros/hab × participação nas admissões **0,707085**. Correlação não demonstra causalidade.
- Normalizados os dois indicadores de intensidade com `log1p` e Min-Max no universo de 760 municípios, combinando pesos 50/50 no `indice_intensidade` (0–100). Maiores índices: Pacaraima/RR **100,00**, Chuí/RS **93,96**, Guatambu/SC **84,06**, Boa Vista/RR **83,96**, Itapiranga/SC **79,42**, Seara/SC **78,81**.
- Comparação dos rankings de volume e intensidade: Spearman **0,502**; **somente 2 municípios comuns aos dois Top 20**: Boa Vista/RR (volume 3º; intensidade 4º) e Chapecó/SC (volume 4º; intensidade 11º).
- Sensibilidade dos pesos no índice de intensidade (60/40, 50/50, 40/60): Spearman entre extremos **0,983** e **16 municípios comuns aos três Top 20**.
- Decisão metodológica: **manter dois rankings separados** — volume e intensidade — para preservar a distinção entre grandes polos e relevância relativa; pesos 50/50 permanecem hipóteses exploratórias.
- Consolidado `ranking_final_2025` com indicadores e posições dos dois índices, mais população 2026. **Usuário confirmou salvamento** de `data/processed/rankings/ranking_municipal_volume_intensidade_2025.parquet` (760 municípios). O código que gerou a exportação foi corrigido para adicionar `populacao_2026` ausente na tabela intermediária.
- **Ressalvas:** população 2026 usada como denominador aproximado de registros administrativos de 2025; índice por habitante não é prevalência de migrantes residentes; participação nas admissões não mede proporção de migrantes empregados nem taxa de empregabilidade; municípios sem registros nas fontes não devem virar automaticamente zeros; escalas Min-Max dependem dos 760 municípios e os valores são relativos a esse universo.

## 20. Módulo 2: comparação municipal por CBO — 03/11/2026
- Criado `06_oportunidades_capacitacao.ipynb`; retomado `caged_atividades` no notebook 02 e agrupadas movimentações de migrantes 2025 por município × CBO: **50.753 combinações**, **393.465 admissões**, **315.556 desligamentos**, saldo **+77.909**, sem códigos IBGE ausentes. Usuário confirmou salvamento de `data/processed/trabalho/emprego_migrantes_municipio_cbo_2025.parquet`.
- Cruzamento `outer` dessa tabela com o CAGED geral município × CBO: **994.623 combinações**, **50.753 correspondentes (`both`)**, 943.870 exclusivas do CAGED geral e **zero exclusivamente migrantes**; sem chaves duplicadas. Entre as 50.753 combinações comparáveis, **zero casos com admissões migrantes maiores que as gerais**; totais migrantes integralmente preservados.
- Produzido `ranking_comparativo_cbo` com admissões gerais/migrantes, percentual de admissões migrantes por ocupação e índice de representação em relação à participação de referência nacional da tabela CBO (aproximadamente **1,50%**). Exemplos: alimentador de linha 52.750 admissões migrantes, participação 3,99% (2,67×); magarefe 17.010, 25,44% (17,02×); abatedor 4.882, 13,79% (9,22×).
- Exploradas combinações município × CBO com filtros **≥100 admissões gerais** e **≥30 migrantes**, ordenadas por participação percentual; nomes/UF recuperados da base municipal. Exemplos: abatedor em Dois Vizinhos/PR (273/295, 92,54%), magarefe em Guatambu/SC (1.569/2.284, 68,70%) e Chapecó/SC (3.653/5.470, 66,78%). Os filtros são exploratórios, não prova de demanda por curso.
- Para exportação posterior de CBO, identificadas **2.447 linhas de município × CBO sem título** (29 códigos; 16.922 admissões gerais e 146 migrantes), incluindo `999999`. Preservados todos os registros; títulos ausentes preenchidos com código e indicação de ausência de descrição, e `999999` como ocupação não identificada.

## 21. Módulo 2: cruzamento emprego × cursos — 03/11/2026
- Recarregada oferta técnica de `educacao_municipio_curso_2025.parquet`: **18.793 combinações**, 6 colunas. Resumo de **14 áreas formativas**: Gestão e negócios 711.071 matrículas; Ambiente e saúde 503.998; Informação e comunicação 424.627; Produção alimentícia 24.535.
- No eixo Produção alimentícia, cursos de Alimentos (**130 municípios, 12.601 matrículas**) e Agroindústria (**99, 8.836**) escolhidos como *proxy exploratória*, sem pretensão de esgotar a oferta formativa.
- Confirmados CBO de abatedor `848505`, magarefe `848520` e retalhador de carne `848525`. Agregadas admissões nas três ocupações por município e cruzadas com ofertas de Alimentos e Agroindústria. Entre os **46 municípios com ≥100 admissões migrantes**, **35 (76,09%)** não tinham oferta *registrada desses dois cursos técnicos* no mesmo município; 11 tinham. Não equivaler a ausência de qualquer capacitação ou demanda reprimida.
- Casos com muitas admissões migrantes nas três ocupações e sem os dois cursos registrados: Cascavel/PR **1.589**, Guatambu/SC **1.569**, Palotina/PR **820**, Maringá/PR **722** e Matelândia/PR **610**.
- Cruzados esses municípios com os rankings exploratórios do Módulo 1: Cascavel 8º em volume/39º em intensidade; Guatambu 95º/3º; Marau 44º/26º; Capinzal 86º/21º; Tapejara 73º/12º.
- **Usuário confirmou a exportação** de `data/processed/oportunidades/comparacao_carnes_educacao_2025.parquet` e `data/processed/oportunidades/candidatos_capacitacao_carnes_2025.parquet`. Não foi validado um mapeamento geral CBO → curso, nem recomendações definitivas.

## 22. Redefinição do produto final — 03/11/2026
- Objetivo da entrega ajustado para **ferramenta interativa de apoio à decisão da UNIESF sobre divulgação/expansão de cursos online**, priorizando visualizações e exploração de indicadores existentes, e **não** prescrições definitivas de municípios/cursos.
- Planejado dashboard **Power BI de 6 páginas**: (1) Visão geral; (2) Distribuição migratória; (3) Mercado de trabalho migrante; (4) Migrantes × mercado geral; (5) Oferta educacional **técnica e ensino superior**; (6) Explorador municipal de oportunidades, com filtros territoriais e mapas.
- Planejado relatório **PDF visual de cerca de 5 páginas**, com metodologia enxuta, mapas/gráficos do dashboard, principais padrões e ressalvas. Mais bases processadas/README de suporte.
- Estimativa de escopo reduzido: **aproximadamente 17 horas adicionais** a partir da redefinição, sujeitas a ajustes conforme implementação e validação do Power BI. O cronograma é estimativa, não execução confirmada.
- Despriorizados módulos de recomendações operacionais detalhadas, mapeamento manual extensivo CBO–cursos, novos índices complexos e análises estatísticas extras.
- Criado/usado `07_preparacao_powerbi.ipynb` para preparar as exportações. **Power BI Desktop ainda não teve importação nem relacionamentos confirmados. PDF ainda não produzido.**

## 23. Consolidação territorial e exportações para Power BI — 03/11/2026
- Recarregada a versão anterior de `indicadores_completos_municipais.parquet` (**4.441 municípios, 30 colunas, zero duplicatas**). Integrado CAGED geral municipal por `outer merge`: **5.567 municípios, 33 colunas**, 5.566 com dados CAGED geral.
- No notebook 04, reutilizada tabela de população estimada IBGE 2026; usuário confirmou exportação de `data/processed/populacao_municipal_2026.parquet`. Integrada à base: **5.567 municípios, 34 colunas, nenhuma população ausente e nenhum código duplicado**.
- Detectadas **1.126 linhas sem nome/UF** após expansão pelo CAGED geral. Reutilizada referência `data/processed/municipios_ibge.parquet` (**5.571 municípios**) e preenchidas geometadados com `combine_first`, resultando em **5.571 municípios, 34 colunas**, sem nome/UF ausente e sem duplicatas; quatro municípios adicionais mantidos com indicadores possivelmente ausentes.
- **Salvos e confirmados:** `data/processed/integrados/indicadores_completos_municipais_v2.parquet` (5.571 × 34), sobrescrito com a versão geograficamente completa; `data/processed/integrados/dim_municipios.parquet` (5.571 × 3).
- Criada `fato_indicadores` (5.571 × 27, sem duplicatas) separada de `dim_municipios` e sem flags antigas de cobertura. Colunas de SISMIGRA renomeadas explicitamente para `registros_migratorios_2024`, `registros_migratorios_2025`, `registros_migratorios_2026_parcial`, etc.; emprego geral e migrante permanecem em colunas distintas. Usuário confirmou exportação em `data/processed/powerbi/fato_indicadores.parquet` e `.csv`, e `dim_municipios.csv`, com CSV delimitado por ponto e vírgula/UTF-8-SIG.
- **CBO para Power BI:** montada `fato_emprego_cbo` (994.623 × 9), zero chaves município × CBO duplicadas; títulos ausentes resolvidos com rótulos de código, sem descartar movimentações; **393.465 admissões migrantes**. Usuário confirmou `data/processed/powerbi/fato_emprego_cbo.parquet` e `.csv`.
- **CNAE para Power BI:** carregado CAGED geral município × subclasse (588.508 linhas) e derivado grupo CNAE pelos três dígitos iniciais da subclasse no formato numérico `XX.X`; agregado em **301.632 município × grupo**, preservando **26.318.285 admissões gerais** e **25.061.582 desligamentos**, zero duplicatas. Integração com migrantes município × grupo: **29.601 `both`**, **272.031 apenas geral**, **zero apenas migrantes**, zero chaves duplicadas; **393.415 admissões** e **315.484 desligamentos migrantes**. Descrições completadas a partir das já existentes em outros municípios; **11 grupos** permaneceram sem descrição no dicionário usado (`1.7, 5.0, 19.1, 26.8, 30.5, 51.3, 64.5, 80.3, 84.3, 99.0, 99.9`) e receberam rótulo de código, sem remoção. **Exportados e confirmados:** `data/processed/powerbi/fato_emprego_cnae.parquet` e `.csv` (**301.632 × 9**).
- **Cursos técnicos para Power BI:** `fato_cursos`, **18.793 × 6**, zero município × curso duplicados, **2.490.145 matrículas**, **3.385 municípios**, **14 áreas**. Usuário confirmou exportação em `data/processed/powerbi/fato_cursos.parquet` e `.csv`.
- **Ensino superior integrado:** já disponível nas colunas de `fato_indicadores`; verificados **3.551 municípios** com informação, cursos presenciais 34.479, IES presenciais somadas por município 3.793 (não IES únicas nacionais), matrículas presenciais 5.037.875, matrículas EAD atribuídas a municípios 5.186.811, ingressantes EAD 3.346.076, matrículas de estrangeiros presenciais 15.981 e EAD 6.939. Não criada tabela superior detalhada adicional.
- **Cinco tabelas CSV confirmadas para o Power BI:** `dim_municipios`, `fato_indicadores`, `fato_emprego_cbo`, `fato_emprego_cnae`, `fato_cursos`. Ainda pendente importação, revisão de tipos, modelagem de relacionamentos, medidas e visualizações.

## Pendências e próxima etapa (não concluídas)
- **Próxima ação imediata:** importar os cinco CSVs de `data/processed/powerbi/` no Power BI Desktop, conferir codificação UTF-8/sep `;`, tipos e relacionamentos por `codigo_ibge`; validar filtros e totais antes de criar medidas e mapas.
- Criar as **seis páginas** do dashboard e o **PDF visual complementar** de aproximadamente cinco páginas. Testar comportamento do mapa brasileiro e da navegação por UF/município; elaborar documentação de fontes, períodos e interpretação.
- Corrigir/rotular **11 grupos CNAE** sem descrição da referência e revisar classificação do código CBO `999999`; não excluir seus registros silenciosamente.
- **Comparabilidade das fontes:** CAGED geral originado somente de `CAGEDMOV`, sem reconciliação de `FOR`/`EXC` e revisões; validar antes de declarar números definitivos. O agregado municipal de migrantes em `fato_indicadores` foi originado de grupo CNAE e exclui 50 admissões/72 desligamentos sem correspondência de subclasse, enquanto `fato_emprego_cbo` inclui todos os 393.465/315.556. Não tratar essa diferença como erro do Power BI.
- **Anos e universos:** SISMIGRA 2024–2026 parcial; emprego 2025; técnico 2025; superior 2024; população estimada 2026. Dados administrativos de migração não representam estoque/pessoas únicas; CAGED mede movimentações de vínculos; dados de EAD territoriais não comprovam oferta local ou residência dos alunos; matrícula não mede demanda por curso; somatório de IES municipais não representa IES únicas nacionais.
- **Modelagem:** `fato_indicadores` tem uma linha por município, e `fato_emprego_cbo`, `fato_emprego_cnae` e `fato_cursos` têm múltiplas. Evitar junção física de todas as tabelas detalhadas e contagem dupla; relacionar pela dimensão municipal com medidas e filtros adequados. Não somar instituições distintas de cursos entre linhas.
- Os índices/rankings de 760 municípios são **exploratórios**, não priorização final nem potencial predito de matrículas. O dashboard deve comunicar cobertura variável e ausências em vez de transformá-las automaticamente em zero.
- Retomar módulos amplos de capacitação, estudo de parcerias e recomendações operacionais apenas em fase futura, se houver interesse e dados adicionais.

---

**Ressalva metodológica geral:** o produto é uma **ferramenta exploratória de apoio à decisão**, não previsão de matrículas nem diagnóstico causal de demanda. Preserve sempre o ano, a população-base e as lacunas de cobertura de cada indicador.