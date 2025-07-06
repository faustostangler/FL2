# Statements Pipeline

The workflow that processes financial statements is split into two stages.

1. `FetchStatementsUseCase` downloads raw rows for each NSD and persists them via
   `SqlAlchemyStatementRowsRepository`. Results are buffered by `SaveStrategy` so
   batches are flushed to the repository incrementally.
2. `ParseAndClassifyStatementsUseCase` converts the stored rows into
   `StatementDTO` objects. `PersistStatementsUseCase` then saves these parsed
   statements using `SqlAlchemyStatementRepository`.

Raw and parsed statements use separate repositories to keep the intermediate
HTML-derived rows isolated from the normalized financial data.
