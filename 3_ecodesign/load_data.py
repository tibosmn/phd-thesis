# Requests
from typing import List
import pandas as pd

# from dataclass import VCPU_IMPACT_AGGREGATED, RAM_IMPACT_AGGREGATED
from helpers_functions import get_unique_labels
from pandas.tseries.offsets import DateOffset

K8S_FOLDER = "data/gitlab/without_energy/k8s/"
KVM_FOLDER = "data/gitlab/without_energy/kvm/"
KVM_LIMITS_FOLDER = "data/gitlab/without_energy/k8s_limits/"

USED_SFX = "_used"
RES_SFX = "_reserved"

VCPU_IMPACT_AGGREGATED = 838.9295238095239 / 1000 / (5 * 365)
RAM_IMPACT_AGGREGATED = 380.0 / 1000 / (5 * 365 * 24 * 60)


def convert_time(dataframe: pd.DataFrame) -> None:
    """
    Convert timestamps to datetime
    """
    dataframe["Time"] = pd.to_datetime(dataframe["Time"], unit="ms", origin="unix")


def convert_ram(array) -> List[float]:
    """
    Convert bytes iec to GiB
    """
    return [d / 1e9 for d in array]


def get_without_time(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Return a dataframe without its Time column
    """
    return dataframe.loc[:, dataframe.columns != "Time"]


def load_memory(folder: str, kind="Requested") -> pd.DataFrame:
    """
    Load and convert memory at given folder
    """
    memory = pd.read_csv(folder + "memory.csv")
    convert_time(memory)
    # Convert bytes iec to GiB
    memory["Memory " + kind] = convert_ram(memory["Memory " + kind])
    memory["Memory Used"] = convert_ram(memory["Memory Used"])

    # Fill na
    memory["Memory " + kind].fillna(method="ffill", inplace=True)
    memory["Memory Used"].fillna(method="ffill", inplace=True)
    return memory


def load_memory_by_label(
    folder: str, kind="requests"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and convert memory by label at given folder
    """
    # Load files
    ram_requests_by_label = pd.read_csv(folder + "memory_" + kind + "_by_label.csv")
    ram_used_by_label = pd.read_csv(folder + "memory_used_by_label.csv")

    # Convert time
    convert_time(ram_requests_by_label)
    convert_time(ram_used_by_label)

    # Fill na
    ram_used_by_label.fillna(method="ffill", inplace=True)
    ram_requests_by_label.fillna(method="ffill", inplace=True)

    # Convert memory
    for label in get_without_time(ram_requests_by_label):
        ram_requests_by_label[label] = convert_ram(ram_requests_by_label[label])

    for label in get_without_time(ram_used_by_label):
        ram_used_by_label[label] = convert_ram(ram_used_by_label[label])

    # Drop migrations column, which is unused by the tests and thus its usage not represented
    if "migrations" in ram_requests_by_label:
        ram_requests_by_label = ram_requests_by_label.drop(columns=["migrations"])
    if "migrations" in ram_used_by_label:
        ram_used_by_label = ram_used_by_label.drop(columns=["migrations"])

    return ram_requests_by_label, ram_used_by_label


def load_cpu(folder: str) -> pd.DataFrame:
    """
    Load and convert memory at given folder
    """
    cpu = pd.read_csv(folder + "cpu.csv")
    # Fill na
    cpu.fillna(method="ffill", inplace=True)
    convert_time(cpu)
    return cpu


def load_cpu_by_label(
    folder: str, kind="requests"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and convert cpu by label at given folder
    """
    # Load files
    cpu_requests_by_label = pd.read_csv(folder + "cpu_" + kind + "_by_label.csv")
    cpu_used_by_label = pd.read_csv(folder + "cpu_used_by_label.csv")

    # Fill na
    cpu_used_by_label.fillna(method="ffill", inplace=True)
    cpu_requests_by_label.fillna(method="ffill", inplace=True)

    # Convert time
    convert_time(cpu_requests_by_label)
    convert_time(cpu_used_by_label)

    # Drop migrations column, which is unused by the tests and thus its usage not represented
    if "migrations" in cpu_requests_by_label:
        cpu_requests_by_label = cpu_requests_by_label.drop(columns=["migrations"])
    if "migrations" in cpu_used_by_label:
        cpu_used_by_label = cpu_used_by_label.drop(columns=["migrations"])

    return cpu_requests_by_label, cpu_used_by_label


def load_network(file: str) -> pd.DataFrame:
    """
    Load and convert given network file
    """
    data = pd.read_csv(file)
    data["Time"] = pd.to_datetime(data["Time"], unit="ms", origin="unix")
    data.fillna(method="ffill", inplace=True)
    data["Total"] = get_without_time(data).sum(axis=1)
    return data


def load_vus(file: str) -> pd.DataFrame:
    """
    Load and convert given k6 virtual users file
    """
    data = pd.read_csv(file)
    data["Time"] = pd.to_datetime(data["Time"], unit="ms", origin="unix")
    # data["VUs"] = data["VUs"].fillna(0)
    return data


def load_rps(file: str) -> pd.DataFrame:
    data = pd.read_csv(file)
    data["Time"] = pd.to_datetime(data["Time"], unit="ms", origin="unix")
    # data["Requests per Second"] = data["Requests per Second"].fillna(0)
    return data


def get_consumed_resources_by_label(
    used: pd.DataFrame, requested: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a dataframe with one resource (ram or cpu) impact by label
    """
    result = pd.DataFrame()
    for label in get_unique_labels(used, requested):
        # Get the max if label in both reserved and used
        if label in used and label in requested:
            result[label] = pd.concat([used[label], requested[label]], axis=1).max(
                axis=1
            )
        # If label only in requested, not used
        elif label in requested:
            result[label] = requested[label]
        # If label only in used, not requested
        else:
            result[label] = used[label]
    return result


def get_lost_resources_by_label(
    used: pd.DataFrame, requested: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a dataframe with one resource (ram or cpu) impact by label
    """
    result = pd.DataFrame()
    for label in get_unique_labels(used, requested):
        # Get the lost if label in both reserved and used
        if label in used and label in requested:
            result[label] = requested[label] - used[label]
            result[label][result[label] < 0] = 0
        # If label only in requested, not used all is lost
        elif label in requested:
            result[label] = requested[label]
        # If only in used, no lost so 0
        elif label in used:
            result[label] = 0
    return result


def get_resources_impact_by_label(
    ram_by_label: pd.DataFrame, cpu_by_label: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a dataframe with cpu an memory impact by label
    """
    result = pd.DataFrame()
    for label in get_unique_labels(ram_by_label, cpu_by_label):
        # Get the max if label in both ram and cpu
        if label in ram_by_label and label in cpu_by_label:
            ram = [memory * RAM_IMPACT_AGGREGATED for memory in ram_by_label[label]]
            cpu = [cpu * VCPU_IMPACT_AGGREGATED for cpu in cpu_by_label[label]]
            result[label] = [x + y for x, y in zip(ram, cpu)]
        # If label only in ram, not cpu
        elif label in ram:
            result[label] = [
                memory * RAM_IMPACT_AGGREGATED for memory in ram_by_label[label]
            ]
        # If label only in cpu, not ram
        else:
            result[label] = [
                cpu * VCPU_IMPACT_AGGREGATED for cpu in cpu_by_label[label]
            ]
    return result


##########
# Memory #
##########

k8s_memory = load_memory(K8S_FOLDER)
kvm_memory = load_memory(KVM_FOLDER)
kvm_limits_memory = load_memory(KVM_LIMITS_FOLDER)

###################
# Memory by label #
###################

k8s_ram_requests_by_label, k8s_ram_used_by_label = load_memory_by_label(
    K8S_FOLDER, kind="requests"
)
kvm_ram_requests_by_label, kvm_ram_used_by_label = load_memory_by_label(
    KVM_FOLDER, kind="requests"
)
kvm_limits_ram_requests_by_label, kvm_limits_ram_used_by_label = load_memory_by_label(
    KVM_LIMITS_FOLDER, kind="requests"
)

#######
# CPU #
#######

k8s_cpu = load_cpu(K8S_FOLDER)
kvm_cpu = load_cpu(KVM_FOLDER)
kvm_limits_cpu = load_cpu(KVM_LIMITS_FOLDER)

################
# CPU by label #
################
k8s_cpu_requests_by_label, k8s_cpu_used_by_label = load_cpu_by_label(
    K8S_FOLDER, kind="requests"
)
kvm_cpu_requests_by_label, kvm_cpu_used_by_label = load_cpu_by_label(
    KVM_FOLDER, kind="requests"
)
kvm_limits_cpu_requests_by_label, kvm_limits_cpu_used_by_label = load_cpu_by_label(
    KVM_LIMITS_FOLDER, kind="requests"
)

#######
# RPS #
#######
rps = {
    "KVM": load_rps(KVM_FOLDER + "requests.csv"),
    "K8S": load_rps(K8S_FOLDER + "requests.csv"),
    "KVM LIMITS": load_rps(KVM_LIMITS_FOLDER + "requests.csv"),
}


#################
# Virtual users #
#################
virtual_users = {
    "KVM": load_vus(KVM_FOLDER + "virtual_users.csv"),
    "K8S": load_vus(K8S_FOLDER + "virtual_users.csv"),
    "KVM LIMITS": load_vus(KVM_LIMITS_FOLDER + "virtual_users.csv"),
}

####################
# Received packets #
####################
received_packets = {
    "KVM": load_network(KVM_FOLDER + "received_packets.csv"),
    "K8S": load_network(K8S_FOLDER + "received_packets.csv"),
    "KVM LIMITS": load_network(KVM_LIMITS_FOLDER + "received_packets.csv"),
}
#####################
# Received bandwith #
#####################
received_bandwith = {
    "KVM": load_network(KVM_FOLDER + "receive_bandwith.csv"),
    "K8S": load_network(K8S_FOLDER + "receive_bandwith.csv"),
    "KVM LIMITS": load_network(KVM_LIMITS_FOLDER + "receive_bandwith.csv"),
}
#######################
# Transmitted packets #
#######################
transmitted_packets = {
    "KVM": load_network(KVM_FOLDER + "transmitted_packets.csv"),
    "K8S": load_network(K8S_FOLDER + "transmitted_packets.csv"),
    "KVM LIMITS": load_network(KVM_LIMITS_FOLDER + "transmitted_packets.csv"),
}

########################
# Transmitted bandwith #
########################
transmit_bandwith = {
    "KVM": load_network(KVM_FOLDER + "transmit_bandwith.csv"),
    "K8S": load_network(K8S_FOLDER + "transmit_bandwith.csv"),
    "KVM LIMITS": load_network(KVM_LIMITS_FOLDER + "transmit_bandwith.csv"),
}

#########
# DATES #
#########
K8S_DATES = k8s_cpu["Time"]
KVM_DATES = kvm_cpu["Time"]
KVM_LIMITS_DATES = kvm_limits_cpu["Time"]
FAKE_DATES = KVM_DATES + DateOffset(hours=13)

##################
# Used resources #
##################
used_resources = {
    "KVM": {
        "Memory": kvm_memory["Memory Used"],
        "CPU": kvm_cpu["CPU Used"],
        "Time": KVM_DATES,
    },
    "K8S": {
        "Memory": k8s_memory["Memory Used"],
        "CPU": k8s_cpu["CPU Used"],
        "Time": K8S_DATES,
    },
    "KVM LIMITS": {
        "Memory": kvm_limits_memory["Memory Used"],
        "CPU": kvm_limits_cpu["CPU Used"],
        "Time": KVM_LIMITS_DATES,
    },
}

###########################
# Used resources by label #
###########################

used_resources_by_label = {
    "KVM": {
        "Memory": get_without_time(kvm_ram_used_by_label),
        "CPU": get_without_time(kvm_cpu_used_by_label),
        "Time": KVM_DATES,
    },
    "K8S": {
        "Memory": get_without_time(k8s_ram_used_by_label),
        "CPU": get_without_time(k8s_cpu_used_by_label),
        "Time": K8S_DATES,
    },
    "KVM LIMITS": {
        "Memory": get_without_time(kvm_limits_ram_used_by_label),
        "CPU": get_without_time(kvm_limits_cpu_used_by_label),
        "Time": KVM_LIMITS_DATES,
    },
}

#########################
# Used resources impact #
#########################
used_impact = {
    "KVM": pd.DataFrame(
        {
            "Time": KVM_DATES,
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED for memory in kvm_memory["Memory Used"]
            ],
            "CPU": [cpu * VCPU_IMPACT_AGGREGATED for cpu in kvm_cpu["CPU Used"]],
        }
    ),
    "K8S": pd.DataFrame(
        {
            "Time": K8S_DATES,
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED for memory in k8s_memory["Memory Used"]
            ],
            "CPU": [cpu * VCPU_IMPACT_AGGREGATED for cpu in k8s_cpu["CPU Used"]],
        }
    ),
    "KVM LIMITS": pd.DataFrame(
        {
            "Time": KVM_LIMITS_DATES,
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED
                for memory in kvm_limits_memory["Memory Used"]
            ],
            "CPU": [cpu * VCPU_IMPACT_AGGREGATED for cpu in kvm_limits_cpu["CPU Used"]],
        }
    ),
}

# Add total column
used_impact["KVM"]["Total"] = used_impact["KVM"].loc[:, ["Memory", "CPU"]].sum(axis=1)
used_impact["K8S"]["Total"] = used_impact["K8S"].loc[:, ["Memory", "CPU"]].sum(axis=1)
used_impact["KVM LIMITS"]["Total"] = (
    used_impact["KVM LIMITS"].loc[:, ["Memory", "CPU"]].sum(axis=1)
)

######################################
# Used resources impact by component #
######################################

used_impact_by_label = {
    "KVM": get_resources_impact_by_label(
        ram_by_label=kvm_ram_used_by_label,
        cpu_by_label=kvm_cpu_used_by_label,
    ),
    "K8S": get_resources_impact_by_label(
        ram_by_label=k8s_ram_used_by_label,
        cpu_by_label=k8s_cpu_used_by_label,
    ),
    "KVM LIMITS": get_resources_impact_by_label(
        ram_by_label=kvm_limits_ram_used_by_label,
        cpu_by_label=kvm_limits_cpu_used_by_label,
    ),
}

used_impact_by_label["KVM"]["Time"] = KVM_DATES
used_impact_by_label["K8S"]["Time"] = K8S_DATES
used_impact_by_label["KVM LIMITS"]["Time"] = KVM_LIMITS_DATES

######################
# Reserved resources #
######################
reserved_resources = {
    "KVM": {
        "Memory": kvm_memory["Memory Requested"],
        "CPU": kvm_cpu["CPU Requested"],
        "Time": KVM_DATES,
    },
    "K8S": {
        "Memory": k8s_memory["Memory Requested"],
        "CPU": k8s_cpu["CPU Requested"],
        "Time": K8S_DATES,
    },
    "KVM LIMITS": {
        "Memory": kvm_limits_memory["Memory Requested"],
        "CPU": kvm_limits_cpu["CPU Requested"],
        "Time": KVM_LIMITS_DATES,
    },
}

###############################
# Reserved resources by label #
###############################
reserved_resources_by_label = {
    "KVM": {
        "Memory": get_without_time(kvm_ram_requests_by_label),
        "CPU": get_without_time(kvm_cpu_requests_by_label),
        "Time": KVM_DATES,
    },
    "K8S": {
        "Memory": get_without_time(k8s_ram_requests_by_label),
        "CPU": get_without_time(k8s_cpu_requests_by_label),
        "Time": K8S_DATES,
    },
    "KVM LIMITS": {
        "Memory": get_without_time(kvm_limits_ram_requests_by_label),
        "CPU": get_without_time(kvm_limits_cpu_requests_by_label),
        "Time": KVM_LIMITS_DATES,
    },
}

#############################
# Reserved resources impact #
#############################
reserved_impact = {
    "KVM": pd.DataFrame(
        {
            "Time": KVM_DATES,
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED
                for memory in kvm_memory["Memory Requested"]
            ],
            "CPU": [cpu * VCPU_IMPACT_AGGREGATED for cpu in kvm_cpu["CPU Requested"]],
        }
    ),
    "K8S": pd.DataFrame(
        {
            "Time": K8S_DATES,
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED
                for memory in k8s_memory["Memory Requested"]
            ],
            "CPU": [cpu * VCPU_IMPACT_AGGREGATED for cpu in k8s_cpu["CPU Requested"]],
        }
    ),
    "KVM LIMITS": pd.DataFrame(
        {
            "Time": KVM_LIMITS_DATES,
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED
                for memory in kvm_limits_memory["Memory Requested"]
            ],
            "CPU": [
                cpu * VCPU_IMPACT_AGGREGATED for cpu in kvm_limits_cpu["CPU Requested"]
            ],
        }
    ),
}

# Add total column
reserved_impact["KVM"]["Total"] = (
    reserved_impact["KVM"].loc[:, ["Memory", "CPU"]].sum(axis=1)
)
reserved_impact["K8S"]["Total"] = (
    reserved_impact["K8S"].loc[:, ["Memory", "CPU"]].sum(axis=1)
)
reserved_impact["KVM LIMITS"]["Total"] = (
    reserved_impact["KVM LIMITS"].loc[:, ["Memory", "CPU"]].sum(axis=1)
)

######################
# Consumed resources #
######################
consumed_resources = {
    "KVM": {
        "Memory": kvm_memory[["Memory Requested", "Memory Used"]].max(axis=1),
        "CPU": kvm_cpu[["CPU Requested", "CPU Used"]].max(axis=1),
    },
    "K8S": {
        "Memory": k8s_memory[["Memory Requested", "Memory Used"]].max(axis=1),
        "CPU": k8s_cpu[["CPU Requested", "CPU Used"]].max(axis=1),
    },
    "KVM LIMITS": {
        "Memory": kvm_limits_memory[["Memory Requested", "Memory Used"]].max(axis=1),
        "CPU": kvm_limits_cpu[["CPU Requested", "CPU Used"]].max(axis=1),
    },
}

###############################
# Consumed resources by label #
###############################
kvm_cpu_consumed_label = get_consumed_resources_by_label(
    used=kvm_cpu_used_by_label, requested=kvm_cpu_requests_by_label
)
k8s_cpu_consumed_label = get_consumed_resources_by_label(
    used=k8s_cpu_used_by_label, requested=k8s_cpu_requests_by_label
)
kvm_limits_cpu_consumed_label = get_consumed_resources_by_label(
    used=kvm_limits_cpu_used_by_label, requested=kvm_limits_cpu_requests_by_label
)

kvm_memory_consumed_label = get_consumed_resources_by_label(
    used=kvm_ram_used_by_label, requested=kvm_ram_requests_by_label
)
k8s_memory_consumed_label = get_consumed_resources_by_label(
    used=k8s_ram_used_by_label, requested=k8s_ram_requests_by_label
)
kvm_limits_memory_consumed_label = get_consumed_resources_by_label(
    used=kvm_limits_ram_used_by_label, requested=kvm_limits_ram_requests_by_label
)

consumed_resources_by_label = {
    "KVM": {
        "Memory": kvm_memory_consumed_label,
        "CPU": kvm_cpu_consumed_label,
    },
    "K8S": {"Memory": k8s_memory_consumed_label, "CPU": k8s_cpu_consumed_label},
    "KVM LIMITS": {
        "Memory": kvm_limits_memory_consumed_label,
        "CPU": kvm_limits_cpu_consumed_label,
    },
}

consumed_resources_by_label["KVM"]["Time"] = KVM_DATES
consumed_resources_by_label["K8S"]["Time"] = K8S_DATES
consumed_resources_by_label["KVM LIMITS"]["Time"] = KVM_LIMITS_DATES

#############################
# Consumed resources impact #
#############################
consumed_impact = {
    "KVM": pd.DataFrame(
        {
            "Time": KVM_DATES,
            "CPU": [
                cpu * VCPU_IMPACT_AGGREGATED
                for cpu in kvm_cpu[["CPU Requested", "CPU Used"]].max(axis=1)
            ],
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED
                for memory in kvm_memory[["Memory Requested", "Memory Used"]].max(
                    axis=1
                )
            ],
        }
    ),
    "K8S": pd.DataFrame(
        {
            "Time": K8S_DATES,
            "CPU": [
                cpu * VCPU_IMPACT_AGGREGATED
                for cpu in k8s_cpu[["CPU Requested", "CPU Used"]].max(axis=1)
            ],
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED
                for memory in k8s_memory[["Memory Requested", "Memory Used"]].max(
                    axis=1
                )
            ],
        }
    ),
    "KVM LIMITS": pd.DataFrame(
        {
            "Time": KVM_LIMITS_DATES,
            "CPU": [
                cpu * VCPU_IMPACT_AGGREGATED
                for cpu in kvm_limits_cpu[["CPU Requested", "CPU Used"]].max(axis=1)
            ],
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED
                for memory in kvm_limits_memory[
                    ["Memory Requested", "Memory Used"]
                ].max(axis=1)
            ],
        }
    ),
}

# Add total column
consumed_impact["KVM"]["Total"] = (
    consumed_impact["KVM"].loc[:, ["Memory", "CPU"]].sum(axis=1)
)
consumed_impact["K8S"]["Total"] = (
    consumed_impact["K8S"].loc[:, ["Memory", "CPU"]].sum(axis=1)
)
consumed_impact["KVM LIMITS"]["Total"] = (
    consumed_impact["KVM LIMITS"].loc[:, ["Memory", "CPU"]].sum(axis=1)
)

##########################################
# Consumed resources impact by component #
##########################################
consumed_impact_by_label = {
    "KVM": get_resources_impact_by_label(
        ram_by_label=kvm_memory_consumed_label,
        cpu_by_label=kvm_cpu_consumed_label,
    ),
    "K8S": get_resources_impact_by_label(
        ram_by_label=k8s_memory_consumed_label,
        cpu_by_label=k8s_cpu_consumed_label,
    ),
    "KVM LIMITS": get_resources_impact_by_label(
        ram_by_label=kvm_limits_memory_consumed_label,
        cpu_by_label=kvm_limits_cpu_consumed_label,
    ),
}

consumed_impact_by_label["KVM"]["Time"] = KVM_DATES
consumed_impact_by_label["K8S"]["Time"] = K8S_DATES
consumed_impact_by_label["KVM LIMITS"]["Time"] = KVM_LIMITS_DATES

##################
# Lost resources #
##################
kvm_cpu_lost = kvm_cpu["CPU Requested"] - kvm_cpu["CPU Used"]
kvm_cpu_lost[kvm_cpu_lost < 0] = 0

k8s_cpu_lost = k8s_cpu["CPU Requested"] - k8s_cpu["CPU Used"]
k8s_cpu_lost[k8s_cpu_lost < 0] = 0

kvm_limits_cpu_lost = kvm_limits_cpu["CPU Requested"] - kvm_limits_cpu["CPU Used"]
kvm_limits_cpu_lost[kvm_limits_cpu_lost < 0] = 0


kvm_memory_lost = kvm_memory["Memory Requested"] - kvm_memory["Memory Used"]
kvm_memory_lost[kvm_memory_lost < 0] = 0

k8s_memory_lost = k8s_memory["Memory Requested"] - k8s_memory["Memory Used"]
k8s_memory_lost[k8s_memory_lost < 0] = 0

kvm_limits_memory_lost = (
    kvm_limits_memory["Memory Requested"] - kvm_limits_memory["Memory Used"]
)
kvm_limits_memory_lost[kvm_limits_memory_lost < 0] = 0


lost_resources = {
    "KVM": {
        "Memory": kvm_memory_lost,
        "CPU": kvm_cpu_lost,
    },
    "K8S": {"Memory": k8s_memory_lost, "CPU": k8s_cpu_lost},
    "KVM LIMITS": {
        "Memory": kvm_limits_memory_lost,
        "CPU": kvm_limits_cpu_lost,
    },
}

##################
# Stolen resources #
##################
kvm_cpu_stolen = kvm_cpu["CPU Used"] - kvm_cpu["CPU Requested"]
kvm_cpu_stolen[kvm_cpu_stolen < 0] = 0

k8s_cpu_stolen = k8s_cpu["CPU Used"] - k8s_cpu["CPU Requested"]
k8s_cpu_stolen[k8s_cpu_stolen < 0] = 0

kvm_limits_cpu_stolen = kvm_limits_cpu["CPU Used"] - kvm_limits_cpu["CPU Requested"]
kvm_limits_cpu_stolen[kvm_limits_cpu_stolen < 0] = 0


kvm_memory_stolen = kvm_memory["Memory Used"] - kvm_memory["Memory Requested"]
kvm_memory_stolen[kvm_memory_stolen < 0] = 0

k8s_memory_stolen = k8s_memory["Memory Used"] - k8s_memory["Memory Requested"]
k8s_memory_stolen[k8s_memory_stolen < 0] = 0

kvm_limits_memory_stolen = (
    kvm_limits_memory["Memory Used"] - kvm_limits_memory["Memory Requested"]
)
kvm_limits_memory_stolen[kvm_limits_memory_stolen < 0] = 0


stolen_resources = {
    "KVM": {
        "Memory": kvm_memory_stolen,
        "CPU": kvm_cpu_stolen,
    },
    "K8S": {"Memory": k8s_memory_stolen, "CPU": k8s_cpu_stolen},
    "KVM LIMITS": {
        "Memory": kvm_limits_memory_stolen,
        "CPU": kvm_limits_cpu_stolen,
    },
}

###########################
# Lost resources by label #
###########################
kvm_cpu_lost_label = get_lost_resources_by_label(
    used=kvm_cpu_used_by_label, requested=kvm_cpu_requests_by_label
)
k8s_cpu_lost_label = get_lost_resources_by_label(
    used=k8s_cpu_used_by_label, requested=k8s_cpu_requests_by_label
)
kvm_limits_cpu_lost_label = get_lost_resources_by_label(
    used=kvm_limits_cpu_used_by_label, requested=kvm_limits_cpu_requests_by_label
)

kvm_memory_lost_label = get_lost_resources_by_label(
    used=kvm_ram_used_by_label, requested=kvm_ram_requests_by_label
)
k8s_memory_lost_label = get_lost_resources_by_label(
    used=k8s_ram_used_by_label, requested=k8s_ram_requests_by_label
)
kvm_limits_memory_lost_label = get_lost_resources_by_label(
    used=kvm_limits_ram_used_by_label, requested=kvm_limits_ram_requests_by_label
)

lost_resources_by_label = {
    "KVM": {
        "Memory": kvm_memory_lost_label,
        "CPU": kvm_cpu_lost_label,
    },
    "K8S": {"Memory": k8s_memory_lost_label, "CPU": k8s_cpu_lost_label},
    "KVM LIMITS": {
        "Memory": kvm_limits_memory_lost_label,
        "CPU": kvm_limits_cpu_lost_label,
    },
}

#########################
# Lost resources impact #
#########################
lost_impact = {
    "KVM": pd.DataFrame(
        {
            "Time": KVM_DATES,
            "Memory": [memory * RAM_IMPACT_AGGREGATED for memory in kvm_memory_lost],
            "CPU": [cpu * VCPU_IMPACT_AGGREGATED for cpu in kvm_cpu_lost],
        }
    ),
    "K8S": pd.DataFrame(
        {
            "Time": K8S_DATES,
            "Memory": [memory * RAM_IMPACT_AGGREGATED for memory in k8s_memory_lost],
            "CPU": [cpu * VCPU_IMPACT_AGGREGATED for cpu in k8s_cpu_lost],
        }
    ),
    "KVM LIMITS": pd.DataFrame(
        {
            "Time": KVM_LIMITS_DATES,
            "Memory": [
                memory * RAM_IMPACT_AGGREGATED for memory in kvm_limits_memory_lost
            ],
            "CPU": [cpu * VCPU_IMPACT_AGGREGATED for cpu in kvm_limits_cpu_lost],
        }
    ),
}

# Add total column
lost_impact["KVM"]["Total"] = lost_impact["KVM"].loc[:, ["Memory", "CPU"]].sum(axis=1)
lost_impact["K8S"]["Total"] = lost_impact["K8S"].loc[:, ["Memory", "CPU"]].sum(axis=1)
lost_impact["KVM LIMITS"]["Total"] = (
    lost_impact["KVM LIMITS"].loc[:, ["Memory", "CPU"]].sum(axis=1)
)

######################################
# Lost resources impact by component #
######################################

lost_impact_by_label = {
    "KVM": get_resources_impact_by_label(
        ram_by_label=kvm_memory_lost_label, cpu_by_label=kvm_cpu_lost_label
    ),
    "K8S": get_resources_impact_by_label(
        ram_by_label=k8s_memory_lost_label, cpu_by_label=k8s_cpu_lost_label
    ),
    "KVM LIMITS": get_resources_impact_by_label(
        ram_by_label=kvm_limits_memory_lost_label,
        cpu_by_label=kvm_limits_cpu_lost_label,
    ),
}

lost_impact_by_label["KVM"]["Time"] = KVM_DATES
lost_impact_by_label["K8S"]["Time"] = K8S_DATES
lost_impact_by_label["KVM LIMITS"]["Time"] = KVM_LIMITS_DATES
