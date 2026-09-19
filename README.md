# Bitcoin Deanonymization — SIH26146

Graph-based transaction analysis, suspicious activity detection, and entity investigation prototype for Smart India Hackathon.

## Project structure

- backend/ — FastAPI service and API schemas
- ml/ — preprocessing, model training, and prediction
- graph/ — transaction graph construction and analysis
- frontend/ — investigation dashboard
- data/ — dataset instructions; raw datasets are kept out of Git
- notebooks/ — exploratory analysis
- docs/ — architecture and dataset documentation

## Development workflow

Use feature branches rather than committing directly to main.

Example branches:
- prachi/ml
- dhruvi/backend
- vrindavan/graph
- shreyas/frontend
- ojas/integration

Keep credentials, large raw datasets, generated files, and local environments out of the repository.
