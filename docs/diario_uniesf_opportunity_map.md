# Diário do projeto — UNIESF Opportunity Map

**Última atualização:** 28/10/2026  
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

## 10. Inventário educacional — iniciado (28/10/2026)
- Inspecionada `data/raw/educacao/` de forma recursiva com `Path.rglob("*.csv")`.
- Confirmados **8 arquivos**: seis do Censo Escolar 2025 (`Tabela_Curso_Tecnico_2025_V2.csv`, `Tabela_Docente_2025_V2.csv`, `Tabela_Escola_2025_V2.csv`, `Tabela_Gestor_Escolar_2025_v2.csv`, `Tabela_Matricula_2025_V2.csv`, `Tabela_Turma_2025_V2.csv`) e dois do ensino superior 2024 (`MICRODADOS_CADASTRO_CURSOS_2024.CSV`, `MICRODADOS_ED_SUP_IES_2024.CSV`).
- Definida a prioridade de exploração: cursos técnicos e escolas, depois cadastro de cursos superiores.
- **A criação do notebook `03_exploracao_educacao.ipynb` foi recomendada, mas ainda não foi confirmada pelo usuário**; nenhuma exploração dos campos educacionais foi relatada como concluída.

## Pendências (não concluídas)
- **Próximo passo:** criar/abrir `notebooks/03_exploracao_educacao.ipynb` e carregar `Tabela_Curso_Tecnico_2025_V2.csv` (testar `encoding="latin1"` e `sep=";"`); verificar `.shape` e `.columns`.
- Explorar e integrar dados de oferta formativa do Censo Escolar 2025 e ensino superior 2024, distinguindo oferta de formação de demanda observada por cursos.
- Retomar o CAGED **2026 (janeiro–julho)** para análises de ocupações CBO e grupos CNAE; comparar com janeiro–julho de 2025, não com o ano completo; posteriormente integrar os resultados.
- Definir critérios e pesos de priorização territorial apenas após avaliar limitações e indicadores educacionais.
- Verificar os códigos CNAE sem correspondência (`9900800`, `8630505`) e documentar formalmente diferenças entre versões das classificações; evitar descrições não verificadas.
- Padronizar identificadores CNAE como texto com zeros à esquerda nas tabelas finais, quando apropriado.
- Exportar as tabelas derivadas de ocupações e seções CNAE, caso ainda não tenham sido salvas.

- **Próxima sessão:** construir indicadores de emprego de migrantes **por município IBGE de 7 dígitos e grupo CNAE**, usando `caged_atividades`. Primeiro identificar as colunas `codigo_ibge`, `grupo` e `saldomovimentacao`, depois agrupar e validar admissões, desligamentos e saldo.
- Verificar os códigos CNAE sem correspondência (`9900800`, `8630505`) e documentar formalmente a diferença entre versões das classificações, se necessário; evitar atribuir descrições não verificadas.
- Padronizar identificadores CNAE como texto com zeros à esquerda em tabelas consolidadas, quando apropriado.
- Exportar as tabelas derivadas de ocupações e seções CNAE caso ainda não tenham sido salvas.
- Explorar os microdados educacionais e integrar as dimensões de migração, emprego e oferta formativa.

---

**Nota metodológica:** SISMIGRA mede registros administrativos migratórios, não necessariamente população migrante residente ou indivíduos únicos. Os dados de 2026 são parciais. Para CAGED, a comparação interanual feita foi janeiro–julho em ambos os anos, com município identificado. Os saldos por grupo CNAE representam vínculos formais líquidos, não demanda observada por cursos.
