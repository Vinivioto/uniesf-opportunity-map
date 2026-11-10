"""Tratamento reproduzível do SISMIGRA, sem inferir pessoas únicas ou datas de estoque."""
from pathlib import Path
import unicodedata

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ARQUIVOS_ANUAIS = {
    2022: 'sismigra_2022.csv',
    2023: 'sismigra_2023.csv',
    2024: 'sismigra_2024.csv',
    2025: 'sismigra_janeiro_dezembro_2025.csv',
    2026: 'sismigra_janeiro_agosto_2026.csv',
}
NAO_INFORMADO = 'NÃO INFORMADO'
MARCADORES = {'', '-', '--', '- 00', '####', 'NÃO ESPECIFICADO',
              'NAO ESPECIFICADO', 'NÃO INFORMADO', 'NAO INFORMADO'}
UFS = set('AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split())
FAIXAS = {
    '0 |-- 15 ANOS': '0-14', '15 |-- 25 ANOS': '15-24',
    '25 |-- 40 ANOS': '25-39', '40 |-- 65 ANOS': '40-64', '65 |-- ANOS': '65+',
}


def chave_texto(valor):
    texto = str(valor).upper().replace('´', "'").replace('’', "'")
    return ''.join(c for c in unicodedata.normalize('NFKD', texto)
                   if not unicodedata.combining(c)).strip()


def limpar_texto(serie):
    return (serie.astype('string').str.normalize('NFC').str.strip()
            .str.replace(r'\s+', ' ', regex=True).str.upper()
            .replace(dict.fromkeys(MARCADORES, pd.NA)))


# Somente grafias/sinônimos observados; categorias históricas e territórios são mantidos.
_GRAFIAS_PAISES = {
    'ÁFRICA DO SUL': ['AFRICA DO SUL'], 'ÁUSTRIA': ['AUSTRIA'],
    'ÍNDIA': ['INDIA'], 'SUÍÇA': ['SUÍCA'], 'COREIA DO SUL': ['CORÉIA DO SUL'],
    'COREIA DO NORTE': ['CORÉIA DO NORTE'], 'PAÍSES BAIXOS': ['HOLANDA'],
    'BELARUS': ['BIELORRÚSSIA'], 'CINGAPURA': ['CINGAPURA-SINGAPURA'],
    'PALESTINA': ['ESTADO DA PALESTINA'], 'REPÚBLICA DOMINICANA': ['REP. DOMINICANA'],
    'AZERBAIJÃO': ['AZERBAIDJÃO'], 'MOLDOVA': ['MOLDÁVIA'], 'VIETNÃ': ['VIETINA'],
    'BAREIN': ['BAREINE'], 'OMÃ': ['OMÃ, SULTANATO DE'], 'MAURÍCIO': ['MAURÍCIO, ILHAS'],
    'SÃO TOMÉ E PRÍNCIPE': ['SAO TOMÉ E PRÍNCIPE'], 'ZIMBÁBUE': ['ZIMBABWE'],
    'MONTENEGRO': ['REP. MONTENEGRO'], 'IUGOSLÁVIA': ['IUGUSLAVIA'],
    'KUWAIT': ['KUAITE'], 'EMIRADOS ÁRABES UNIDOS': ['EMIRADOS ÁRABES'],
    'BOTSUANA': ['BOTSWANA'], 'REPÚBLICA CENTRO AFRICANA': ['REP. CENTRO AFRICANA'],
    'FIJI': ['FIJI, ILHAS'], 'BAHAMAS': ['BAHAMA,IS'], 'COMORES': ['COMORES, ILHAS'],
    'PAPUA-NOVA GUINÉ': ['PAPUA, NOVA GUINÉ'], 'ILHAS MARSHALL': ['MARSHALL, ILHAS'],
    'MICRONÉSIA': ['ESTADOS FEDERADOS DA MICRONÉSIA'],
    'ANTÍGUA E BARBUDA': [], 'ANTILHAS HOLANDESAS': [], 'APÁTRIDA': [],
    'NÍGER': [], 'SÃO CRISTÓVÃO E NÉVIS': [],
}
ALIASES_PAISES = {
    chave_texto(grafia): nome
    for nome, grafias in _GRAFIAS_PAISES.items() for grafia in [nome, *grafias]
}


def padronizar_pais(serie):
    valores = limpar_texto(serie).fillna(NAO_INFORMADO)
    mapa = {v: ALIASES_PAISES.get(chave_texto(v), v) for v in valores.unique()}
    return valores.map(mapa).astype('string')


def id_pais(serie):
    return serie.map({v: chave_texto(v) for v in serie.unique()}).astype('string')


def referencia_municipal(raiz):
    """Reutiliza a referência local do projeto; requer chave municipal única."""
    referencia = pd.read_parquet(Path(raiz) / 'data/processed/municipios_ibge.parquet')
    referencia = referencia[['codigo_ibge', 'municipio', 'uf']].copy()
    referencia['codigo_ibge'] = referencia['codigo_ibge'].astype('Int64')
    referencia['chave_municipio'] = limpar_texto(referencia['municipio']).map(chave_texto)
    assert not referencia['codigo_ibge'].duplicated().any()
    assert not referencia.duplicated(['uf', 'chave_municipio']).any()
    return referencia


_CORRECOES_MUNICIPIOS = {
    'SANTANA DO LIVRAMENTO': "SANT'ANA DO LIVRAMENTO",
    'HERVAL DOESTE': "HERVAL D'OESTE", 'PARATI': 'PARATY',
    'SANTA BÁRBARA DOESTE': "SANTA BÁRBARA D'OESTE",
    'ITAPEJARA DOESTE': "ITAPEJARA D'OESTE", 'ESPIGÃO DOESTE': "ESPIGÃO D'OESTE",
    'SANTO ANTÔNIO DO LEVERGER': 'SANTO ANTÔNIO DE LEVERGER',
    'MIRASSOL DOESTE': "MIRASSOL D'OESTE", 'ESTRELA DOESTE': "ESTRELA D'OESTE",
    'EMBU': 'EMBU DAS ARTES', 'ALTA FLORESTA DOESTE': "ALTA FLORESTA D'OESTE",
    'MOJI MIRIM': 'MOGI MIRIM',
}
CORRECOES_MUNICIPIOS = {chave_texto(k): chave_texto(v) for k, v in _CORRECOES_MUNICIPIOS.items()}


def limpar_anual(bruto, ano, referencia):
    """Preserva todas as linhas; flags distinguem cobertura e ausências."""
    obrigatorias = {'DATAREGISTRO', 'UNIDADE_FED_RESIDENCIA', 'MUNICIPIO_RESIDENCIA',
                    'PAIS_NASCIMENTO', 'PAIS_NACIONALIDADE', 'SEXO', 'STATUS'}
    faltantes = obrigatorias - set(bruto.columns)
    if faltantes:
        raise ValueError(f'{ano}: colunas ausentes: {sorted(faltantes)}')
    anos = pd.to_numeric(bruto['DATAREGISTRO'], errors='coerce')
    if not anos.eq(ano).all():
        raise ValueError(f'{ano}: DATAREGISTRO contém ano diferente/ausente')
    df = bruto.copy()
    df['ano_registro'] = ano
    df['periodo'] = f'{ano}-01 a {ano}-08' if ano == 2026 else f'{ano}-01 a {ano}-12'
    df['periodo_completo'] = ano != 2026
    df['tipo_base'] = 'REGISTROS_ANUAIS'
    df['uf'] = limpar_texto(df['UNIDADE_FED_RESIDENCIA'])
    df['uf_informada_valida'] = df['uf'].isin(UFS)
    df['uf'] = df['uf'].where(df['uf_informada_valida'], 'NI')
    municipio = limpar_texto(df['MUNICIPIO_RESIDENCIA'])
    df['municipio_informado'] = municipio.notna()
    chaves = municipio.dropna().unique()
    mapa = {v: CORRECOES_MUNICIPIOS.get(chave_texto(v), chave_texto(v)) for v in chaves}
    df['chave_municipio'] = municipio.map(mapa)
    # Reutiliza a correspondência explícita São Luiz/RR -> 1400605 do notebook original.
    chave_sao_luiz = referencia.loc[referencia['codigo_ibge'].eq(1400605), 'chave_municipio'].iloc[0]
    df.loc[(df['chave_municipio'] == 'SAO LUIZ') & (df['uf'] == 'RR'), 'chave_municipio'] = chave_sao_luiz
    df = df.merge(referencia[['codigo_ibge', 'municipio', 'uf', 'chave_municipio']],
                  on=['uf', 'chave_municipio'], how='left', validate='many_to_one')
    df['MUNICIPIO_PADRONIZADO'] = df['municipio'].fillna(municipio.reset_index(drop=True))
    df['geografia_municipal_valida'] = df['codigo_ibge'].notna()
    df['pais_origem'] = padronizar_pais(df['PAIS_NASCIMENTO'])
    df['pais_nacionalidade'] = padronizar_pais(df['PAIS_NACIONALIDADE'])
    df['pais_origem_id'] = id_pais(df['pais_origem'])
    df['pais_nacionalidade_id'] = id_pais(df['pais_nacionalidade'])
    df['sexo'] = limpar_texto(df['SEXO']).fillna(NAO_INFORMADO)
    df['situacao'] = limpar_texto(df['STATUS']).fillna(NAO_INFORMADO)
    classificacao = 'CLASSIFICACAO_REVISADA' if 'CLASSIFICACAO_REVISADA' in df else 'CLASSIFICACAO_REGISTRO'
    df['classificacao'] = limpar_texto(df[classificacao]).fillna(NAO_INFORMADO)
    if 'IDADE' in df:
        idade = pd.to_numeric(df['IDADE'], errors='coerce')
        df['idade_invalida'] = idade.lt(0)
        faixa = pd.cut(idade.where(idade.ge(0)), [0, 15, 25, 40, 65, float('inf')],
                       labels=['0-14', '15-24', '25-39', '40-64', '65+'], right=False)
        df['FAIXA_ETARIA'] = faixa.astype('string').fillna('Não especificado')
    else:
        df['idade_invalida'] = False
        faixa = limpar_texto(df['FAIXA_ETARIA']).replace(FAIXAS)
        esperadas = set(FAIXAS.values())
        if not faixa.dropna().isin(esperadas).all():
            raise ValueError(f'{ano}: faixa etária não reconhecida')
        df['FAIXA_ETARIA'] = faixa.fillna('Não especificado')
    df['faixa_etaria'] = df['FAIXA_ETARIA']
    entrada = pd.to_numeric(df['DATAENTRADA'], errors='coerce')
    df['ano_entrada'] = entrada.where(entrada.between(1, ano) & entrada.mod(1).eq(0)).astype('Int64')
    df['ano_entrada_invalido_ou_ausente'] = df['ano_entrada'].isna()
    assert len(df) == len(bruto), 'Limpeza não pode perder registros'
    return df.drop(columns='chave_municipio')


def contar(dados, chaves, medida='registros'):
    return dados.groupby(chaves, dropna=False, observed=True).size().reset_index(name=medida)


def participacao(tabela, grupos, medida='registros'):
    tabela = tabela.copy()
    total = tabela.groupby(grupos, dropna=False)[medida].transform('sum')
    tabela['participacao_pct'] = tabela[medida].div(total).mul(100)
    return tabela


def exportar(tabela, destino, nome, csv=False):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    tabela.to_parquet(destino / f'{nome}.parquet', index=False)
    if csv:
        tabela.to_csv(destino / f'{nome}.csv', sep=';', encoding='utf-8-sig', index=False)


def processar_anuais(raiz):
    raiz = Path(raiz)
    destino = raiz / 'data/processed/migracao'
    referencia = referencia_municipal(raiz)
    tabelas = {nome: [] for nome in [
        'fato_migracao_pais_ano', 'fato_migracao_nacionalidade_ano',
        'fato_migracao_uf_pais_ano', 'fato_migracao_municipio_pais_ano',
        'fato_migracao_municipio_ano', 'fato_migracao_perfil_ano',
    ]}
    qualidade, pendencias, grafias = [], [], []
    for ano, arquivo in ARQUIVOS_ANUAIS.items():
        bruto = pd.read_csv(raiz / 'data/raw/migracao' / arquivo,
                            sep=';', encoding='utf-8', low_memory=False)
        df = limpar_anual(bruto, ano, referencia)
        territorial = df[df['uf_informada_valida'] & df['municipio_informado']]
        qualidade.append({
            'ano_registro': ano, 'arquivo': arquivo, 'registros_brutos': len(bruto),
            'registros_tratados': len(df), 'linhas_identicas_excedentes': int(bruto.duplicated().sum()),
            'uf_ausente_ou_invalida': int((~df['uf_informada_valida']).sum()),
            'municipio_nao_informado': int((~df['municipio_informado']).sum()),
            'sem_codigo_ibge': int(df['codigo_ibge'].isna().sum()),
            'com_codigo_ibge': int(df['codigo_ibge'].notna().sum()),
            'pais_nascimento_nao_informado': int(df['pais_origem'].eq(NAO_INFORMADO).sum()),
            'pais_nacionalidade_nao_informado': int(df['pais_nacionalidade'].eq(NAO_INFORMADO).sum()),
            'faixa_etaria_nao_informada': int(df['faixa_etaria'].eq('Não especificado').sum()),
            'idades_negativas': int(df['idade_invalida'].sum()),
            'ano_entrada_invalido_ou_ausente': int(df['ano_entrada_invalido_ou_ausente'].sum()),
        })
        exportar(df, destino, f'sismigra_{ano}_completo')
        # Mantém o contrato das bases territoriais já consumidas no projeto.
        exportar(territorial, destino, f'sismigra_{ano}')
        periodo = ['ano_registro', 'periodo', 'periodo_completo', 'tipo_base']
        municipal = df[df['geografia_municipal_valida']]
        especificacoes = {
            'fato_migracao_pais_ano': (df, ['pais_origem_id', 'pais_origem']),
            'fato_migracao_nacionalidade_ano': (df, ['pais_nacionalidade_id', 'pais_nacionalidade']),
            'fato_migracao_uf_pais_ano': (df, ['uf', 'pais_origem_id', 'pais_origem']),
            'fato_migracao_municipio_pais_ano': (municipal, ['codigo_ibge', 'pais_origem_id', 'pais_origem']),
            'fato_migracao_municipio_ano': (municipal, ['codigo_ibge']),
            'fato_migracao_perfil_ano': (df, ['pais_origem_id', 'pais_origem', 'sexo', 'faixa_etaria', 'situacao', 'classificacao']),
        }
        for nome, (dados, chaves) in especificacoes.items():
            resumo = contar(dados, periodo + chaves)
            assert resumo['registros'].sum() == len(dados), nome
            tabelas[nome].append(resumo)
        faltantes = contar(df[df['codigo_ibge'].isna()],
                          ['ano_registro', 'uf', 'MUNICIPIO_RESIDENCIA'])
        pendencias.append(faltantes)
        for original, limpo in [('PAIS_NASCIMENTO', 'pais_origem'), ('PAIS_NACIONALIDADE', 'pais_nacionalidade')]:
            mapa = df[[original, limpo]].drop_duplicates().rename(columns={original: 'valor_original', limpo: 'pais_padronizado'})
            grafias.append(mapa.assign(arquivo=arquivo, coluna=original))
        print(f'{ano}: {len(df):,} registros; {len(municipal):,} com código IBGE')
    resultado = {nome: pd.concat(partes, ignore_index=True) for nome, partes in tabelas.items()}
    for nome in ['fato_migracao_pais_ano', 'fato_migracao_nacionalidade_ano']:
        resultado[nome] = participacao(resultado[nome], ['ano_registro'])
    resultado['fato_migracao_uf_pais_ano'] = participacao(resultado['fato_migracao_uf_pais_ano'], ['ano_registro', 'uf'])
    resultado['fato_migracao_municipio_pais_ano'] = participacao(resultado['fato_migracao_municipio_pais_ano'], ['ano_registro', 'codigo_ibge'])
    # Crescimento nacional por país apenas entre anos completos consecutivos.
    for nome, coluna in [('fato_migracao_pais_ano', 'pais_origem_id'),
                         ('fato_migracao_nacionalidade_ano', 'pais_nacionalidade_id')]:
        atual = resultado[nome]
        anterior = atual[atual['periodo_completo']][[coluna, 'ano_registro', 'registros']].copy()
        anterior['ano_registro'] += 1
        anterior = anterior.rename(columns={'registros': 'registros_ano_anterior'})
        atual = atual.merge(anterior, on=[coluna, 'ano_registro'], how='left', validate='one_to_one')
        comparavel = atual['periodo_completo'] & atual['registros_ano_anterior'].gt(0)
        atual['variacao_absoluta'] = (atual['registros'] - atual['registros_ano_anterior']).where(comparavel)
        atual['variacao_pct'] = (atual['registros'].div(atual['registros_ano_anterior']) - 1).mul(100).where(comparavel)
        resultado[nome] = atual
    for nome, tabela in resultado.items():
        exportar(tabela, destino, nome)
    qualidade = pd.DataFrame(qualidade)
    pendencias = pd.concat(pendencias, ignore_index=True)
    grafias = pd.concat(grafias, ignore_index=True)
    exportar(qualidade, destino, 'qualidade_sismigra_anual', csv=True)
    exportar(pendencias, destino, 'pendencias_geograficas_sismigra', csv=True)
    exportar(grafias, destino, 'grafias_paises_sismigra', csv=True)
    # Formato largo compatível com os notebooks 02/04; mantém a variação 2024–2025.
    municipal = resultado['fato_migracao_municipio_ano']
    comparacao = municipal.pivot(index='codigo_ibge', columns='ano_registro', values='registros').fillna(0)
    comparacao.columns = [str(c) if c != 2026 else '2026_parcial' for c in comparacao.columns]
    comparacao = comparacao.reset_index().merge(referencia[['codigo_ibge', 'municipio', 'uf']], on='codigo_ibge', validate='one_to_one')
    comparacao['variacao_absoluta'] = comparacao['2025'] - comparacao['2024']
    comparacao['variacao_%'] = comparacao['variacao_absoluta'].div(comparacao['2024'].where(comparacao['2024'].gt(0))).mul(100).round(2)
    exportar(comparacao, destino, 'indicadores_migracao_municipal')
    return {**resultado, 'qualidade': qualidade, 'pendencias': pendencias, 'grafias': grafias, 'comparacao': comparacao}


def processar_ativos(raiz, tamanho_lote=200_000):
    """Lê o arquivo por lotes, conserva todas as situações e exporta o recorte ATIVO."""
    raiz = Path(raiz)
    arquivo = raiz / 'data/raw/migracao/sismigra_ativos.csv'
    destino = raiz / 'data/processed/migracao'
    destino.mkdir(parents=True, exist_ok=True)
    chaves = ['uf', 'pais_id', 'pais_fonte', 'sexo', 'situacao', 'classificacao', 'tipologia_amparos', 'amparo']
    partes, grafias, ausencias = [], [], []
    total = uf_ausente = pais_ausente = 0
    writer = None
    try:
        for bruto in pd.read_csv(arquivo, sep=';', encoding='utf-8', dtype='string', chunksize=tamanho_lote):
            esperadas = {'unidade_da_federacao', 'pais', 'amparo', 'descricao_amparo', 'classificacao', 'sexo', 'tipologia_amparos', 'situacao'}
            if not esperadas.issubset(bruto.columns):
                raise ValueError('Estrutura inesperada do SISMIGRA ativos')
            df = bruto.copy()
            df['uf'] = limpar_texto(bruto['unidade_da_federacao'])
            invalida = ~df['uf'].isin(UFS)
            uf_ausente += int(invalida.sum())
            df['uf'] = df['uf'].where(~invalida, 'NI')
            df['pais_fonte'] = padronizar_pais(bruto['pais'])
            df['pais_id'] = id_pais(df['pais_fonte'])
            pais_ausente += int(df['pais_fonte'].eq(NAO_INFORMADO).sum())
            for coluna in ['sexo', 'situacao', 'classificacao', 'tipologia_amparos', 'amparo']:
                df[coluna] = limpar_texto(df[coluna]).fillna(NAO_INFORMADO)
            df['tipo_base'] = 'CADASTRO_POR_SITUACAO'
            df['criterio_pais'] = 'PAIS_DA_FONTE_SEM_DEFINICAO'
            df['snapshot_id'] = 'sismigra_ativos_sem_data_referencia'
            tabela_arrow = pa.Table.from_pandas(df, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(destino / 'sismigra_ativos_tratado.parquet', tabela_arrow.schema)
            writer.write_table(tabela_arrow)
            partes.append(contar(df, chaves))
            grafias.append(df[['pais', 'pais_fonte']].drop_duplicates().rename(columns={'pais': 'valor_original', 'pais_fonte': 'pais_padronizado'}))
            ausencias.append(pd.DataFrame({'coluna': bruto.columns, 'nulos_originais': bruto.isna().sum().values}))
            total += len(df)
    finally:
        if writer is not None:
            writer.close()
    completo = pd.concat(partes, ignore_index=True).groupby(chaves, as_index=False, dropna=False)['registros'].sum()
    completo['tipo_base'] = 'CADASTRO_POR_SITUACAO'
    completo['criterio_pais'] = 'PAIS_DA_FONTE_SEM_DEFINICAO'
    completo['snapshot_id'] = 'sismigra_ativos_sem_data_referencia'
    assert completo['registros'].sum() == total
    resumo = completo.groupby('situacao', as_index=False)['registros'].sum()
    ativos = completo[completo['situacao'].eq('ATIVO')]
    uf_pais = ativos.groupby(['uf', 'pais_id', 'pais_fonte', 'snapshot_id', 'criterio_pais'], as_index=False)['registros'].sum()
    uf_pais = participacao(uf_pais, ['uf'])
    pais = ativos.groupby(['pais_id', 'pais_fonte', 'snapshot_id', 'criterio_pais'], as_index=False)['registros'].sum()
    pais['participacao_pct'] = pais['registros'].div(pais['registros'].sum()).mul(100)
    assert uf_pais['registros'].sum() == resumo.loc[resumo.situacao.eq('ATIVO'), 'registros'].sum()
    qualidade = pd.DataFrame([{
        'arquivo': arquivo.name, 'registros_brutos': total, 'registros_tratados': int(completo.registros.sum()),
        'registros_situacao_ativo': int(ativos.registros.sum()), 'uf_ausente_ou_invalida': uf_ausente,
        'pais_nao_informado': pais_ausente, 'data_referencia_informada': False,
        'combinacoes_dimensoes': len(completo),
        'linhas_excedentes_mesmas_dimensoes': total - len(completo),
    }])
    resultado = {'fato_sismigra_situacao': completo, 'fato_sismigra_ativos_uf_pais': uf_pais,
                 'fato_sismigra_ativos_pais': pais, 'qualidade_sismigra_ativos': qualidade,
                 'situacoes_sismigra': resumo}
    for nome, tabela in resultado.items():
        exportar(tabela, destino, nome)
    mapa = pd.concat(grafias, ignore_index=True).drop_duplicates()
    exportar(mapa, destino, 'grafias_paises_sismigra_ativos', csv=True)
    ausencias = pd.concat(ausencias).groupby('coluna', as_index=False)['nulos_originais'].sum()
    exportar(ausencias, destino, 'ausencias_sismigra_ativos', csv=True)
    print(f'Cadastro: {total:,} registros; situação ATIVO: {ativos.registros.sum():,}')
    return {**resultado, 'grafias': mapa, 'ausencias': ausencias}


def exportar_powerbi_migracao(raiz):
    raiz = Path(raiz)
    origem = raiz / 'data/processed/migracao'
    destino = raiz / 'data/processed/powerbi'
    nomes = [
        'fato_migracao_pais_ano', 'fato_migracao_nacionalidade_ano',
        'fato_migracao_uf_pais_ano', 'fato_migracao_municipio_pais_ano',
        'fato_migracao_municipio_ano', 'fato_migracao_perfil_ano',
        'fato_sismigra_situacao', 'fato_sismigra_ativos_uf_pais', 'fato_sismigra_ativos_pais',
    ]
    paises = []
    manifesto = []
    for nome in nomes:
        df = pd.read_parquet(origem / f'{nome}.parquet')
        exportar(df, destino, nome, csv=True)
        manifesto.append({'tabela': nome, 'linhas': len(df), 'registros': int(df.registros.sum())})
        for chave, rotulo in [('pais_origem_id', 'pais_origem'), ('pais_nacionalidade_id', 'pais_nacionalidade'), ('pais_id', 'pais_fonte')]:
            if chave in df:
                paises.append(df[[chave, rotulo]].rename(columns={chave: 'pais_id', rotulo: 'pais'}))
    dim_paises = pd.concat(paises).drop_duplicates().sort_values('pais_id').reset_index(drop=True)
    assert not dim_paises.pais_id.duplicated().any(), 'Chave de país ambígua'
    # Não são códigos ISO e a dimensão inclui categorias não geográficas.
    dim_paises['categoria_nao_geografica'] = dim_paises.pais_id.isin(['NAO INFORMADO', 'APATRIDA', 'NACIONALIDADE INDEFINIDA'])
    exportar(dim_paises, destino, 'dim_paises', csv=True)
    dim_anos = pd.DataFrame([
        {'ano_registro': ano, 'mes_inicio': 1, 'mes_fim': 8 if ano == 2026 else 12,
         'periodo_completo': ano != 2026, 'tipo_base': 'REGISTROS_ANUAIS'}
        for ano in ARQUIVOS_ANUAIS
    ])
    exportar(dim_anos, destino, 'dim_periodos_migracao', csv=True)
    ufs = pd.DataFrame({'uf': sorted(UFS) + ['NI']})
    ufs['uf_informada'] = ufs.uf.ne('NI')
    exportar(ufs, destino, 'dim_ufs', csv=True)
    return pd.DataFrame(manifesto)
