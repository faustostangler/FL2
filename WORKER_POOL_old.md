# WorkerPool Callbacks

`WorkerPool.run` provides two optional callbacks to handle results:

- `on_result(item: R)`: Invoked for every item returned by the worker. Use it for incremental persistence, real-time progress updates, or in-place validation and enrichment.
- `post_callback(items: List[R])`: Executed once after all workers finish. Use it for final batch persistence, consolidated reporting, or cleanup logic.

A common pattern is to pass a save callback via `on_result` for periodic flushes and rely on `post_callback` for the final flush and summary metrics. This keeps the worker pool generic while allowing callers to handle persistence and reporting according to their own needs.
