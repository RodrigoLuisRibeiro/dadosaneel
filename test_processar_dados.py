import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
from deltalake import DeltaTable, write_deltalake

import processar_dados as pipeline


class TestGravacaoDelta(unittest.TestCase):
    def test_substitui_esquema_legado_sem_persistir_indice(self):
        indicadores = (
            'DEC DECINC DECIND DECINE DECINO DECIP DECIPC DECXN DECXNC '
            'DECXP DECXPC FEC FECINC FECIND FECINE FECINO FECIP FECIPC '
            'FECXN FECXNC FECXP FECXPC NumCon DIC FIC'
        ).split()
        registro = {nome: 1.0 for nome in indicadores}
        registro.update(Distribuidora='TESTE', CNPJ='123', ConjuntoID='1',
                        Ano=2024, Mes=1, NomConjunto='Conjunto teste')
        atual = pd.DataFrame([registro])
        legado = atual.copy()
        legado.index = pd.Index([7])

        with tempfile.TemporaryDirectory() as destino:
            write_deltalake(destino, legado, partition_by=['Ano', 'Distribuidora'])
            self.assertEqual(len(DeltaTable(destino).schema().fields), 32)
            configuracao = {**pipeline.config, 'paths': {'processed_data': destino}}
            with patch.object(pipeline, 'config', configuracao), \
                 patch.object(pipeline, 'processar_dados_locais', return_value=atual), \
                 patch.object(pipeline, 'processar_dados_api', return_value=atual):
                # A deduplicação deixa um índice não contíguo: ele não deve ser salvo.
                pipeline.criar_pipeline_unificado()
                tabela = DeltaTable(destino)
                self.assertEqual(len(tabela.schema().fields), 31)
                self.assertNotIn('__index_level_0__',
                                 [campo.name for campo in tabela.schema().fields])
                self.assertEqual(sum(tabela.get_add_actions().column('num_records').to_pylist()), 1)
                self.assertEqual(tabela.metadata().partition_columns,
                                 ['Ano', 'Distribuidora'])
                pipeline.criar_pipeline_unificado()
                self.assertEqual(sum(DeltaTable(destino).get_add_actions()
                                     .column('num_records').to_pylist()), 1)


if __name__ == '__main__':
    unittest.main()
