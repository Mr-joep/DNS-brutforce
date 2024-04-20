import csv
import datetime
import dns.resolver
import itertools
import threading
import os

# Function to perform DNS lookup for a subdomain
def dns_lookup(subdomain, domain, results):
    try:
        result = dns.resolver.resolve(subdomain + '.' + domain, 'A')
        ip_address = result[0].to_text()
        results.append((subdomain + '.' + domain, ip_address))
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.NXDOMAIN:
        pass
    except dns.exception.Timeout:
        pass

# Function to generate subdomains
def generate_subdomains(domain, max_length):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789-'
    subdomains = [''.join(sub) for sub in itertools.product(characters, repeat=max_length)]
    return subdomains

# Main program
def main():
    # Prompt user for maximum length of subdomains
    max_length = int(input("Enter the maximum length of subdomains: "))

    # Initialize DNS resolver
    resolver = dns.resolver.Resolver()

    # Generate subdomains
    domain = "google.com"  # Change this to your desired domain
    subdomains = generate_subdomains(domain, max_length)

    # Container for results
    results = []

    # Perform DNS lookups concurrently using threads
    threads = []
    for subdomain in subdomains:
        thread = threading.Thread(target=dns_lookup, args=(subdomain, domain, results))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Save results to CSV file with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = "results"
    os.makedirs(folder, exist_ok=True)
    csv_file = os.path.join(folder, f"DNS_lookup_results_{timestamp}.csv")

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Subdomain', 'IP Address'])
        writer.writerows(results)

    print(f"DNS lookups completed. Results saved in: {csv_file}")

# Entry point of the script
if __name__ == "__main__":
    main()
