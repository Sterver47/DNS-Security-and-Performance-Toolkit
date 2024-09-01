import time
import random
from ping3 import ping
import dns.resolver
import pandas as pd
import numpy as np
import os

# Configuration variables
INTERVAL = 60  # in seconds
DURATION = None  # None for continuous measurement
OUTPUT_FILE = 'dns_latency_results.csv'
PING_LATENCY = True
DNS_QUERY_LATENCY = True
ANALYSIS_INTERVAL = 600  # Print analysis every 10 minutes
GOOGLE_DOMAIN = 'google.com'  # Always query google.com


# Load DNS servers from file
def load_dns_servers(file_path='dns_servers.txt'):
    with open(file_path, 'r') as file:
        dns_servers = [line.strip() for line in file if line.strip()]
    return dns_servers


# Load domains from file
def load_domains(file_path='new_domains.txt'):
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains


# Measure ping latency
def measure_ping_latency(server):
    try:
        latency = ping(server)
        return latency if latency is not None else np.nan
    except Exception:
        return np.nan  # Suppress error messages


# Measure DNS query latency
def measure_dns_query_latency(server, domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    try:
        start_time = time.time()
        resolver.resolve(domain)
        latency = time.time() - start_time
        return latency
    except Exception:
        return np.nan  # Suppress error messages


# Basic analysis function for the measurement tool
def basic_analysis(file_path='dns_latency_results.csv'):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print("No data available for analysis.")
        return

    df = pd.read_csv(file_path)

    if df.empty:
        print("No data available for analysis.")
        return

    # Calculate mean latencies and NaN counts
    summary = df.groupby('server').agg({
        'ping_latency': ['mean', lambda x: x.isna().sum()],
        'google_query_latency': ['mean', lambda x: x.isna().sum()],
        'domain_query_latency': ['mean', lambda x: x.isna().sum()],
    })

    summary.columns = ['ping_latency_mean', 'ping_latency_nan_count',
                       'google_query_latency_mean', 'google_query_latency_nan_count',
                       'domain_query_latency_mean', 'domain_query_latency_nan_count']

    # Print the basic statistics
    print("\nBasic Statistics (Average Latency in Seconds):")
    print(summary[['ping_latency_mean', 'google_query_latency_mean', 'domain_query_latency_mean']])
    print("\nNumber of Failed Pings/Queries:")
    print(summary[['ping_latency_nan_count', 'google_query_latency_nan_count', 'domain_query_latency_nan_count']])


# Run the measurement process
def run_measurements(dns_servers, domains, interval, duration, output_file='results.csv', analysis_interval=3600):
    start_time = time.time()
    next_analysis_time = start_time + analysis_interval

    with open(output_file, 'a') as file:
        if os.path.getsize(output_file) == 0:  # Add headers if the file is new
            file.write('timestamp,server,ping_latency,google_query_latency,domain_query_latency,domain\n')

        while duration is None or time.time() < start_time + duration:
            # Pick one random domain for all servers during this interval
            selected_domain = random.choice(domains)

            print(f"Measurement started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", end='')

            for server in dns_servers:
                ping_latency = measure_ping_latency(server) if PING_LATENCY else None

                # Measure google.com
                google_latency = measure_dns_query_latency(server, GOOGLE_DOMAIN) if DNS_QUERY_LATENCY else None

                # Measure the selected random domain
                domain_latency = measure_dns_query_latency(server, selected_domain) if DNS_QUERY_LATENCY else None

                # Log all measurements in a single CSV line per server
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                file.write(f'{timestamp},{server},{ping_latency},{google_latency},{domain_latency},{selected_domain}\n')

                # Print a dot for each server
                print('.', end='')

            print()  # Print a newline after all servers are processed

            if time.time() >= next_analysis_time:
                print('Running periodic analysis...')
                basic_analysis(output_file)
                next_analysis_time += analysis_interval

            time.sleep(interval + random.uniform(-0.1, 0.1) * interval)


if __name__ == "__main__":
    dns_servers = load_dns_servers()
    domains = load_domains()
    run_measurements(dns_servers, domains, INTERVAL, DURATION, OUTPUT_FILE, ANALYSIS_INTERVAL)
