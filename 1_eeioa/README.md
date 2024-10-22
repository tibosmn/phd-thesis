# EEIOA (Environmentally extended input–output analysis)

This folder contains the source code to download and use [EXIOBASE](https://www.exiobase.eu) EEIOA data.
To use notebook files, create a venv and install requirements as follows:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

To download complete EXIOBASE industry by industry data between 1995 and 2022, run (requires wget):

```bash
cd exio3
./dl.sh
```

[!WARNING]  
This represents 22Gb of data

Temporal data cannot be uploaded due to GitHub file limit of 100mb. To generate the data, use `python data/create_temporal_data.py`
