"""Leitura dos arquivos ativos da tabela Delta para o dashboard."""
from deltalake import DeltaTable
import pyarrow as pa
import pyarrow.dataset as ds


def nomes_distribuidoras(tabela):
    return tabela.get_add_actions(flatten=True).column('partition.Distribuidora').to_pylist()


def listar_distribuidoras(path='dados_processados'):
    return sorted({nome.strip() for nome in nomes_distribuidoras(DeltaTable(path))
                   if nome and nome.strip()})


def ler_distribuidora(distribuidora, path='dados_processados'):
    tabela = DeltaTable(path)
    # O seletor mostra nomes sem espaços, mas as partições legadas os preservam.
    nomes = sorted({nome for nome in nomes_distribuidoras(tabela)
                    if nome and nome.strip() == distribuidora.strip()})
    dataset = tabela.to_pyarrow_dataset()
    valores = pa.array(nomes, type=dataset.schema.field('Distribuidora').type)
    return dataset.to_table(filter=ds.field('Distribuidora').isin(valores),
                            use_threads=False).to_pandas()
