import tempfile
import unittest

import pandas as pd
from deltalake import write_deltalake

from dados_dashboard import ler_distribuidora, listar_distribuidoras


class TestLeituraDelta(unittest.TestCase):
    def test_ignora_versoes_antigas_e_resolve_espacos_nas_particoes(self):
        with tempfile.TemporaryDirectory() as path:
            antigo = pd.DataFrame({'Distribuidora': ['EMPRESA ', 'REMOVIDA'],
                                   'Ano': [2024, 2024], 'DEC': [99.0, 88.0]})
            atual = pd.DataFrame({'Distribuidora': ['EMPRESA ', 'EMPRESA', 'OUTRA'],
                                 'Ano': [2024, 2025, 2025], 'DEC': [1.0, 2.0, 3.0]})
            write_deltalake(path, antigo, partition_by=['Ano', 'Distribuidora'])
            write_deltalake(path, atual, mode='overwrite',
                            partition_by=['Ano', 'Distribuidora'])
            self.assertEqual(listar_distribuidoras(path), ['EMPRESA', 'OUTRA'])
            resultado = ler_distribuidora('EMPRESA', path)
            self.assertEqual(sorted(resultado['DEC'].tolist()), [1.0, 2.0])
            self.assertTrue(ler_distribuidora('REMOVIDA', path).empty)


if __name__ == '__main__':
    unittest.main()
