from infrastructure.config import Config


def test_statements_config_loads():
    config = Config()
    assert config.statements.statement_items[0]["grupo"] == "Dados da Empresa"
    assert "INFORMACOES TRIMESTRAIS" in config.statements.nsd_type_map
