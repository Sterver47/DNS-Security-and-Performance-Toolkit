import dns.resolver
import time
import csv
import datetime
import random


# Function to resolve a domain using a specific DNS server
def resolve_domain(domain, dns_server, sleep_time):
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        answer = resolver.resolve(domain, 'A')
        ip_address = answer[0].to_text()
        time.sleep(sleep_time)
        return ip_address != '0.0.0.0'
    except Exception:
        return False


# Function to load already processed domains from working_domains.txt
def load_processed_domains(working_domains_file):
    try:
        with open(working_domains_file, 'r') as wdf:
            return set(wdf.read().splitlines())
    except FileNotFoundError:
        return set()


# Main function to evaluate DNS servers
def evaluate_dns_servers(domains_file, dns_servers_file, working_domains_file, csv_output_file, sleep_time,
                         num_domains):
    # Load already processed domains
    processed_domains = load_processed_domains(working_domains_file)

    # Read domains and DNS servers from files
    with open(domains_file, 'r') as df:
        all_domains = df.read().splitlines()

    with open(dns_servers_file, 'r') as dsf:
        dns_servers = dsf.read().splitlines()

    # Select X random domains
    domains = random.sample(all_domains, num_domains)

    total_domains = len(domains)
    total_resolvable_domains = 0
    dns_stats = {dns: {'resolved': 0, 'blocked': 0} for dns in dns_servers}

    start_time = datetime.datetime.now()

    try:
        # Open CSV file for appending
        with open(csv_output_file, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write header only if the file is new
            if csvfile.tell() == 0:
                header = ['Domain'] + dns_servers
                csvwriter.writerow(header)

            for index, domain in enumerate(domains, start=1):
                if domain in processed_domains:
                    print(f"Domain '{domain}' already processed. Skipping...")
                    continue

                row = [domain]
                domain_resolved = False
                for dns_server in dns_servers:
                    resolved = resolve_domain(domain, dns_server, sleep_time)
                    row.append(resolved)
                    if resolved:
                        dns_stats[dns_server]['resolved'] += 1
                        domain_resolved = True
                    else:
                        dns_stats[dns_server]['blocked'] += 1

                if domain_resolved:
                    total_resolvable_domains += 1
                    # Append domain to working_domains_file
                    with open(working_domains_file, 'a') as wdf:
                        wdf.write(f"{domain}\n")
                    processed_domains.add(domain)

                csvwriter.writerow(row)

                # Progress and time estimation
                completed = index
                remaining = total_domains - completed
                elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
                estimated_time = (elapsed_time / completed) * remaining
                print(
                    f"Tested {completed}/{total_domains} domains. Remaining: {remaining} domains. "
                    f"Estimated time left: {datetime.timedelta(seconds=estimated_time)} "
                    f"Domain: '{domain}' was {'RESOLVED' if domain_resolved else 'not resolved'}."
                )

                # Print intermediate stats after every 10 domains
                if completed % 10 == 0:
                    print("\n" + "=" * 50)
                    print("Intermediate DNS Servers Stats:")
                    for dns_server, stats in dns_stats.items():
                        blocked_due_to_resolving_issues = total_resolvable_domains - stats['resolved']
                        print(
                            f"{dns_server}: {stats['resolved']} domains RESOLVED, {blocked_due_to_resolving_issues} domains BLOCKED")
                    print("=" * 50 + "\n")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    finally:
        end_time = datetime.datetime.now()
        duration = end_time - start_time

        # Print final statistics
        print("\nFinal Statistics:")
        print(f"Start of the test: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End of the test: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration of the test: {str(duration)}")
        print(
            f"Domains tested: {total_domains} (randomly picked domains from total of {len(all_domains)} domains)")
        print(f"Active domains: {total_resolvable_domains} (resolved by at least one of the DNS servers)")

        print("\nDNS Servers Stats:")
        for dns_server, stats in dns_stats.items():
            blocked_due_to_resolving_issues = total_resolvable_domains - stats['resolved']
            print(
                f"{dns_server}: {stats['resolved']} domains RESOLVED, {blocked_due_to_resolving_issues} domains BLOCKED")


if __name__ == "__main__":
    # Input/Output files
    domains_file = "domains.txt"  # list of domains to check for
    dns_servers_file = "dns_servers.txt"  # list of DNS servers
    working_domains_file = "working_domains.txt"  # already processed active domains (have A record)
    csv_output_file = "dns_results.csv"  # detailed output
    sleep_time = 0  # seconds between checking if needed
    num_domains = 1904  # Number of random domains to pick from the domain_file

    evaluate_dns_servers(domains_file, dns_servers_file, working_domains_file, csv_output_file, sleep_time, num_domains)
