# Ecodesign

This repository contains the script to deploy Gitlab and the socialnetwork app on a k3d Kubernetes cluster using helm-charts, as well as a static deployment of Gitlab.

- To deploy deathstarbenchmark/socialnetwork, follow instructions in [deathstarbench/README.md](./deathstarbench/README.md)
- To deploy Gitlab Helm chart, follow instructions in [gitlab/cluster/README.md](./gitlab/cluster/README.md)
- To deploy Gitlab using VMs, follow instructions in [gitlab/KVM/README.md](./gitlab/KVM/README.md)

---

To use the Jupyter notebooks, first install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

[!WARNING]
Influx energy monitoring file is too large for GitHub size limit 100mb, and thus not included