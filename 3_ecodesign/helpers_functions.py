from typing import List
from kubernetes import client, config
import pandas as pd


def get_unique_labels(df1: pd.DataFrame, df2: pd.DataFrame) -> List[str]:
    """
    Return the unique labels between two dataframes
    """
    df0 = df1.keys().append(df2.keys())
    if "Time" in df0:
        df0 = df0.drop(["Time"])
    return list(df0.unique())


def translate_suffix(value: str) -> float:
    """
    Convert value with suffix to float,
     following suffixes given in
     https://github.com/kubernetes/kubernetes/blob/8fd414537b5143ab039cb910590237cabf4af783/pkg/api/resource/suffix.go#L108
    """
    if value.endswith("Ki"):
        return float(value.replace("Ki", "")) * (2**10)
    elif value.endswith("Mi"):
        return float(value.replace("Mi", "")) * (2**20)
    elif value.endswith("Gi"):
        return float(value.replace("Gi", "")) * (2**30)
    elif value.endswith("Ti"):
        return float(value.replace("Ti", "")) * (2**40)
    elif value.endswith("Pi"):
        return float(value.replace("Pi", "")) * (2**50)
    elif value.endswith("Ei"):
        return float(value.replace("Ei", "")) * (2**60)

    elif value.endswith("n"):
        return float(value.replace("n", "")) * (10**-9)
    elif value.endswith("u"):
        return float(value.replace("u", "")) * (10**-6)
    elif value.endswith("m"):
        return float(value.replace("m", "")) * (10**-3)

    elif value.endswith("k"):
        return float(value.replace("k", "")) * (10**3)
    elif value.endswith("M"):
        return float(value.replace("M", "")) * (10**6)
    elif value.endswith("G"):
        return float(value.replace("G", "")) * (10**9)
    elif value.endswith("T"):
        return float(value.replace("T", "")) * (10**12)
    elif value.endswith("P"):
        return float(value.replace("P", "")) * (10**15)
    elif value.endswith("E"):
        return float(value.replace("E", "")) * (10**18)
    else:
        return float(value)


def translate_memory_str(value: str) -> float:
    """
    Take a memory value as str,
     return it as a GB float
     following https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-memory
    First convert it to bytes, then to GB
    """
    return translate_suffix(value) * (10**9)


def translate_cpu_str(value: str) -> float:
    """
    Take a cpu value as str, return it as a CPU float unit (% of vCPU)
     following https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu
    """
    return translate_suffix(value)


PodName = str
PodUsage = dict[str, List[float]]
PodsUsage = dict[PodName, PodUsage]


def list_pods():
    """
    Connect to kutectl api and return all pods in "default" namespace, where Gitlab ressources are
    """
    config.load_kube_config()
    cust = client.CustomObjectsApi()
    return cust.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "pods")


def get_pod_usage(pod) -> tuple[float, float]:
    """
    From a pod usage dict defined by metrics.k8s.io,
     return its cpu and ram consumption as floats,
     by summing all its containers consumptions
    """
    cpu_total = 0.0
    ram_total = 0.0
    for container in pod["containers"]:
        cpu_total += translate_cpu_str(container["usage"]["cpu"])
        ram_total += translate_memory_str(container["usage"]["memory"])

    return cpu_total, ram_total


def update_pods_usage(pods_usage: PodsUsage) -> PodsUsage:
    pods = list_pods()

    for pod in pods["items"]:
        pod_name = pod["metadata"]["name"]

        if pod_name not in pods_usage:
            pods_usage[pod_name] = {"cpu": [], "memory": []}

        cpu_pod, ram_pod = get_pod_usage(pod)
        pods_usage[pod_name]["cpu"].append(cpu_pod)
        pods_usage[pod_name]["memory"].append(ram_pod)


def get_pods_reservation():
    pods_reservation = {}
    config.load_kube_config()
    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False)

    for pod in ret.items:
        pod_name = pod.metadata.name
        cpu_pod = 0.0
        ram_pod = 0.0

        if pod_name not in pods_reservation:
            pods_reservation[pod_name] = {"cpu": 0.0, "memory": 0.0}
        for container in pod.spec.containers:
            request = container.resources.requests
            if request is not None:
                if "cpu" in request:
                    cpu_pod += translate_cpu_str(request["cpu"])
                if "memory" in request:
                    ram_pod += translate_memory_str(request["memory"])

        pods_reservation[pod_name]["cpu"] += cpu_pod
        pods_reservation[pod_name]["memory"] += ram_pod
    return pods_reservation
