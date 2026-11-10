"""Valida regras que poderiam alterar contagens ou misturar universos SISMIGRA."""
from pathlib import Path
import tempfile
import unittest

import pandas as pd
import pyarrow.parquet as pq

from src.migracao import (
    NAO_INFORMADO, chave_texto, limpar_anual, padronizar_pais, processar_ativos,
)


class LimpezaAnualTest(unittest.TestCase):
    def setUp(self):
        self.referencia = pd.DataFrame({
            'codigo_ibge': pd.Series([1400605, 4122803], dtype='Int64'),
            'municipio': ['SÃO LUIZ DO ANAUÁ', "ITAPEJARA D'OESTE"],
            'uf': ['RR', 'PR'],
            'chave_municipio': [chave_texto('SÃO LUIZ DO ANAUÁ'), chave_texto("ITAPEJARA D'OESTE")],
        })
        self.base = pd.DataFrame({
            'DATAREGISTRO': [2026] * 4,
            'DATAENTRADA': ['2025', '####', '2027', '2026'],
            'UNIDADE_FED_RESIDENCIA': ['RR', 'PR', '-', 'SP'],
            'MUNICIPIO_RESIDENCIA': ['SÃO LUIZ', 'ITAPEJARA D´OESTE', 'NÃO ESPECIFICADO', 'SÃO LUIZ'],
            'PAIS_NASCIMENTO': [' INDIA ', 'ÍNDIA', '-', 'CONGO'],
            'PAIS_NACIONALIDADE': ['ÍNDIA', 'PORTUGAL', None, 'REPÚBLICA DEMOCRÁTICA DO CONGO'],
            'IDADE': [-1950, 25, None, 65],
            'SEXO': ['Feminino'] * 4, 'STATUS': ['Ativo'] * 4,
            'CLASSIFICACAO_REVISADA': ['RESIDENTE'] * 4,
        })

    def test_geografia_por_uf_e_apostrofo_sem_adivinhar_municipio(self):
        df = limpar_anual(self.base, 2026, self.referencia)
        self.assertEqual(len(df), 4)
        self.assertEqual(df.loc[0, 'codigo_ibge'], 1400605)
        self.assertEqual(df.loc[1, 'codigo_ibge'], 4122803)
        self.assertTrue(pd.isna(df.loc[3, 'codigo_ibge']))
        self.assertEqual(df.loc[2, 'uf'], 'NI')

    def test_idade_invalida_e_periodo_parcial_preservam_registros(self):
        df = limpar_anual(self.base, 2026, self.referencia)
        self.assertEqual(df.loc[0, 'faixa_etaria'], 'Não especificado')
        self.assertTrue(df.loc[0, 'idade_invalida'])
        self.assertEqual(df.loc[1, 'faixa_etaria'], '25-39')
        self.assertEqual(df.loc[3, 'faixa_etaria'], '65+')
        self.assertFalse(df.periodo_completo.any())
        self.assertTrue(pd.isna(df.loc[2, 'ano_entrada']))

    def test_nascimento_e_nacionalidade_sao_conservados_separadamente(self):
        df = limpar_anual(self.base, 2026, self.referencia)
        self.assertEqual(df.loc[0, 'pais_origem'], 'ÍNDIA')
        self.assertEqual(df.loc[2, 'pais_origem'], NAO_INFORMADO)
        self.assertEqual(df.loc[3, 'pais_origem'], 'CONGO')
        self.assertEqual(df.loc[3, 'pais_nacionalidade'], 'REPÚBLICA DEMOCRÁTICA DO CONGO')
        self.assertEqual(df.loc[0, 'PAIS_NASCIMENTO'], ' INDIA ')

    def test_ano_inconsistente_e_interrompido(self):
        self.base.loc[0, 'DATAREGISTRO'] = 2025
        with self.assertRaises(ValueError):
            limpar_anual(self.base, 2026, self.referencia)

    def test_grafias_equivalentes_sem_fundir_categorias_historicas(self):
        paises = padronizar_pais(pd.Series(['HOLANDA', 'PAÍSES BAIXOS', 'SUÍCA', 'SUÍÇA',
                                          'CONGO', 'REPÚBLICA DEMOCRÁTICA DO CONGO',
                                          'UNIÃO SOVIÉTICA', 'RÚSSIA']))
        self.assertEqual(paises[0], paises[1])
        self.assertEqual(paises[2], paises[3])
        self.assertNotEqual(paises[4], paises[5])
        self.assertNotEqual(paises[6], paises[7])


class CadastroAtivoTest(unittest.TestCase):
    def test_filtro_explicito_e_reconciliacao_entre_lotes(self):
        # Linhas iguais em lotes diferentes precisam continuar contando separadamente.
        diretorio_testes = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=diretorio_testes) as pasta:
            raiz = Path(pasta)
            assert raiz.resolve().is_relative_to(diretorio_testes)
            raw = raiz / 'data/raw/migracao'
            raw.mkdir(parents=True)
            base = pd.DataFrame({
                'unidade_da_federacao': ['SP', 'SP', None, 'SP', 'SP'],
                'pais': ['ÍNDIA', 'ÍNDIA', None, 'ÍNDIA', 'ÍNDIA'],
                'amparo': ['14'] * 5, 'descricao_amparo': ['Exemplo'] * 5,
                'classificacao': ['TEMPORáRIO'] * 5, 'sexo': ['Feminino'] * 5,
                'tipologia_amparos': ['OUTROS'] * 5,
                'situacao': ['Ativo', 'Cancelado', 'Ativo', 'Prazo vencido', 'Ativo'],
            })
            base.to_csv(raw / 'sismigra_ativos.csv', sep=';', index=False)
            resultado = processar_ativos(raiz, tamanho_lote=2)
            self.assertEqual(resultado['fato_sismigra_situacao'].registros.sum(), 5)
            self.assertEqual(resultado['fato_sismigra_ativos_uf_pais'].registros.sum(), 3)
            self.assertEqual(resultado['fato_sismigra_ativos_pais'].registros.sum(), 3)
            self.assertEqual(resultado['fato_sismigra_situacao'].classificacao.unique().tolist(), ['TEMPORÁRIO'])
            tratado = raiz / 'data/processed/migracao/sismigra_ativos_tratado.parquet'
            self.assertEqual(pq.read_metadata(tratado).num_rows, 5)
            self.assertEqual(resultado['qualidade_sismigra_ativos'].iloc[0].pais_nao_informado, 1)


if __name__ == '__main__':
    unittest.main()
