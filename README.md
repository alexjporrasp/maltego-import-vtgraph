# maltego-import-vtgraph
Script to save VirusTotal Graphs as Maltego CSV tables.

## Requirements

1. Intall Python 3.
2. Sign up/Log in at VirusTotal and save your API key in an OS environment variable
called "VIRUSTOTAL_API_KEY".

## Usage

```
python3 .../vt_to_maltego.py <vtgraph_id> <output_csv>
```

where <vtgraph_id> refers to the ID of the graph you want to import and <output_csv>
refers to the path of the out CSV file.