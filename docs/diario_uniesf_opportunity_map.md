# Diário do projeto — UNIESF Opportunity Map

**Última atualização:** 22/10/2026  
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

## Pendências (não concluídas)
- **Próxima sessão:** construir indicadores de emprego de migrantes **por município IBGE de 7 dígitos e grupo CNAE**, usando `caged_atividades`. Primeiro identificar as colunas `codigo_ibge`, `grupo` e `saldomovimentacao`, depois agrupar e validar admissões, desligamentos e saldo.
- Verificar os códigos CNAE sem correspondência (`9900800`, `8630505`) e documentar formalmente a diferença entre versões das classificações, se necessário; evitar atribuir descrições não verificadas.
- Padronizar identificadores CNAE como texto com zeros à esquerda em tabelas consolidadas, quando apropriado.
- Exportar as tabelas derivadas de ocupações e seções CNAE caso ainda não tenham sido salvas.
- Explorar os microdados educacionais e integrar as dimensões de migração, emprego e oferta formativa.

---

**Nota metodológica:** SISMIGRA mede registros administrativos migratórios, não necessariamente população migrante residente ou indivíduos únicos. Os dados de 2026 são parciais. Para CAGED, a comparação interanual feita foi janeiro–julho em ambos os anos, com município identificado. Os saldos por grupo CNAE representam vínculos formais líquidos, não demanda observada por cursos.
