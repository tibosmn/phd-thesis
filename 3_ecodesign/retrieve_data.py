import influxdb_client
import csv
import datetime
import requests
import pandas as pd
import argparse
from datetime import timedelta

# Define the time range
# start_time = (
#     (datetime.datetime.now() - datetime.timedelta(hours=1)).astimezone().isoformat()
# )
# end_time = datetime.datetime.now(timezone.utc).astimezone().isoformat()

# Set up argument parser
parser = argparse.ArgumentParser(description="Parse two datetime arguments")

# Add arguments for the two datetime strings
parser.add_argument(
    "start_datetime",
    type=datetime.datetime.fromisoformat,
    help="Start datetime in format YYYY-MM-DD HH:MM:SS",
)
parser.add_argument(
    "end_datetime",
    type=datetime.datetime.fromisoformat,
    help="End datetime in format YYYY-MM-DD HH:MM:SS",
)


def round_to_down_minute(dt):
    # Determine if we need to round up or down
    # if dt.second >= 30:
    #     # If 30 seconds or more, round up to the next minute
    #     dt = dt + timedelta(minutes=1)
    # Set seconds and microseconds to zero
    return dt.replace(second=0, microsecond=0)


# Parse the arguments
args = parser.parse_args()
start_time = round_to_down_minute(args.start_datetime).isoformat()
end_time = round_to_down_minute(args.end_datetime).isoformat()

print(start_time)
print(end_time)
step = "30s"  # Query resolution step (e.g., 30 seconds)

############
# INFLUXDB #
############

# influx_bucket = "power_consumption"
# influx_org = "influxdata"
# influx_token = "influxdbtoken"
# influx_url = "http://influxdb.kubernetes"
# influx_csv_file_path = "data/influx.csv"

# influx_client = influxdb_client.InfluxDBClient(
#     url=influx_url, token=influx_token, org=influx_org, timeout=10**6
# )

# influx_query_api = influx_client.query_api()
# # influx_query = (
# #     'from(bucket: "'
# #     + influx_bucket
# #     + '") \
# #   |> range(start: '
# #     + str(start_time)
# #     + ", stop: "
# #     + str(end_time)
# #     + ") \
# #   |> aggregateWindow(every: "
# #     + step
# #     + ', fn: mean, createEmpty: false) \
# #   |> filter(fn: (r) => r["_measurement"] == "power_consumption") \
# #   |> filter(fn: (r) => r["_field"] == "power") \
# #   |> filter(fn: (r) => r["namespace"] == "default") \
# #   |> group(columns: ["_time", "target"])  // Group by timestamp and target \
# #   |> sum(column: "_value")  // Sum the values for each group \
# #   |> yield(name: "mean")'
# # )

# influx_query = (
#     'from(bucket: "'
#     + influx_bucket
#     + '") \
#   |> range(start: '
#     + str(start_time)
#     + ", stop: "
#     + str(end_time)
#     + ')\
#   |> filter(fn: (r) => r["_measurement"] == "power_consumption")\
#   |> filter(fn: (r) => r["_field"] == "power")\
#   |> filter(fn: (r) => r["namespace"] == "default")\
#   |> group(columns: ["target"])\
#   |> aggregateWindow(every: '
#     + step
#     + ', fn: mean, createEmpty: false)\
#   |> yield(name: "mean")'
# )


# influx_result = influx_query_api.query(org=influx_org, query=influx_query)
# print(influx_result)
# # Write query results to CSV
# with open(influx_csv_file_path, mode="w", newline="") as file:
#     writer = csv.writer(file)

#     # Check if there are any records
#     if influx_result:
#         # Get the first record to retrieve all field names dynamically
#         first_record = influx_result[0].records[0]
#         headers = first_record.values.keys()  # Extract headers from the first record

#         # Write the header row to the CSV
#         writer.writerow(headers)

#         # Write all records to the CSV
#         for table in influx_result:
#             for record in table.records:
#                 writer.writerow(record.values.values())  # Write each record's values

# print(f"Influx data has been written to {influx_csv_file_path}")


##############
# PROMETHEUS #
##############

prom_url = "http://prometheus.some.domain/"
prom_namespace = "default"
time = "2m"


# Memory
########
prom_memory_used_query = (
    'sum by (container)(\
            container_memory_working_set_bytes{namespace="'
    + prom_namespace
    + '", container!="", image!=""}\
        )'
)
prom_memory_limits_query = (
    'sum by (container)(\
            kube_pod_container_resource_limits{namespace="'
    + prom_namespace
    + '", resource="memory"}\
        )'
)
prom_memory_requests_query = (
    'sum by (container)(\
            kube_pod_container_resource_requests{namespace="'
    + prom_namespace
    + '", resource="memory"}\
        )'
)

# CPU
########
prom_cpu_used_query = (
    'sum by (container)(\
            rate(container_cpu_usage_seconds_total{namespace="'
    + prom_namespace
    + '", image !="", container!=""}['
    + time
    + "])\
        )"
)
prom_cpu_limits_query = (
    'sum by (container)(\
            kube_pod_container_resource_limits{namespace="'
    + prom_namespace
    + '", resource="cpu"}\
        )'
)
prom_cpu_requests_query = (
    'sum by (container)(\
            kube_pod_container_resource_requests{namespace="'
    + prom_namespace
    + '", resource="cpu"}\
        )'
)

prom_receive_bandwith_query = (
    'sum by (pod)(\
            rate(container_network_receive_bytes_total{namespace="'
    + prom_namespace
    + '", image !=""}['
    + time
    + "])\
        )"
)
prom_transmit_bandwith_query = (
    'sum by (pod)(\
        rate(container_network_transmit_bytes_total{namespace="'
    + prom_namespace
    + '", image !=""}['
    + time
    + "])\
    )"
)

prom_mem_used_csv_file_path = "data/gitlab/prometheus_mem_used.csv"
prom_mem_requests_csv_file_path = "data/gitlab/prometheus_mem_requests.csv"
prom_mem_limits_csv_file_path = "data/gitlab/prometheus_mem_limits.csv"
prom_cpu_used_csv_file_path = "data/gitlab/prometheus_cpu_used.csv"
prom_cpu_requests_csv_file_path = "data/gitlab/prometheus_cpu_requests.csv"
prom_cpu_limits_csv_file_path = "data/gitlab/prometheus_cpu_limits.csv"
prom_receive_csv_file_path = "data/gitlab/prometheus_receive.csv"
prom_transmit_csv_file_path = "data/gitlab/prometheus_transmit.csv"

# Construct the API URL
prom_api_url = f"{prom_url}/api/v1/query_range"

for prom_query, csv_path in zip(
    [
        prom_memory_used_query,
        prom_memory_requests_query,
        prom_memory_limits_query,
        prom_cpu_used_query,
        prom_cpu_requests_query,
        prom_cpu_limits_query,
        prom_receive_bandwith_query,
        prom_transmit_bandwith_query,
    ],
    [
        prom_mem_used_csv_file_path,
        prom_mem_requests_csv_file_path,
        prom_mem_limits_csv_file_path,
        prom_cpu_used_csv_file_path,
        prom_cpu_requests_csv_file_path,
        prom_cpu_limits_csv_file_path,
        prom_receive_csv_file_path,
        prom_transmit_csv_file_path,
    ],
):

    # Define the parameters for the query
    prom_params = {
        "query": prom_query,
        "start": start_time,
        "end": end_time,
        "step": step,
    }
    # Make the request to the Prometheus API
    response = requests.get(prom_api_url, params=prom_params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        result = response.json()

        # Extract the 'result' field from the JSON response
        data = result.get("data", {}).get("result", [])

        if data:
            # Create a dictionary to store the data
            data_dict = {}
            # Process the data
            for entry in data:
                pod_name = (
                    entry["metric"]["container"]
                    if "container" in entry["metric"]
                    else entry["metric"]["pod"]
                )
                for timestamp, value in entry["values"]:
                    if timestamp not in data_dict:
                        data_dict[timestamp] = {}
                    data_dict[timestamp][pod_name] = value

            # Convert the dictionary to a DataFrame
            df = pd.DataFrame.from_dict(data_dict, orient="index")

            # Sort the DataFrame by timestamp (index)
            df.sort_index(inplace=True)

            # Save the DataFrame to a CSV file
            df.to_csv(csv_path, index_label="timestamp")

            print("Data has been saved to " + csv_path)
        else:
            print("No data returned from Prometheus.")
    else:
        print(
            f"Error: Unable to fetch data from Prometheus (status code: {response.status_code}), (response: {response.content})"
        )
