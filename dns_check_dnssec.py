import dns.resolver
import dns.query
import dns.dnssec
import dns.message


def check_dnssec(server, domain="iana.org"):
    try:
        # Create a DNS query
        query = dns.message.make_query(domain, dns.rdatatype.DNSKEY, want_dnssec=True)

        # Send the query to the specified DNS server
        response = dns.query.udp(query, server, timeout=5)

        # Check if the AD flag (Authenticated Data) is set
        if response.flags & dns.flags.AD:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error querying DNS server {server}: {e}")
        return False


def main():
    # Read the list of DNS servers from the file
    with open("dns_servers.txt", "r") as file:
        dns_servers = [line.strip() for line in file.readlines()]

    for server in dns_servers:
        if check_dnssec(server):
            print(f"DNS server {server} supports DNSSEC.")
        else:
            print(f"DNS server {server} does not support DNSSEC.")


if __name__ == "__main__":
    main()
