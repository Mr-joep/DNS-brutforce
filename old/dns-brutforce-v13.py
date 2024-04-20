import csv
import dns.resolver
import concurrent.futures
from datetime import datetime
import os

def dns_lookup(subdomains, resolver):
    results = []
    for subdomain in subdomains:
        try:
            answers = resolver.resolve(subdomain, 'A')
            for answer in answers:
                if str(answer) != "NXDOMAIN":
                    results.append([subdomain, str(answer)])
        except:
            pass

    return results

def generate_subdomains(characters, max_length):
    subdomains = set()
    for length in range(1, max_length + 1):
        for i in range(len(characters) ** length):
            subdomain = ''
            index = i
            for _ in range(length):
                subdomain = characters[index % len(characters)] + subdomain
                index //= len(characters)
            subdomains.add(subdomain + '.google.com')
    return list(subdomains)

def main():
    characters = "abcdefghijklmnopqrstuvwxyz0123456789-"
    max_length = int(input("Enter the maximum length of subdomains: "))

    subdomains = generate_subdomains(characters, max_length)

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['1.1.1.1']  # Use local DNS server at IP 192.168.11.5

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_subdomain = {executor.submit(dns_lookup, [subdomain], resolver): subdomain for subdomain in subdomains}
        for future in concurrent.futures.as_completed(future_to_subdomain):
            subdomain = future_to_subdomain[future]
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"Error processing {subdomain}: {e}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = "raw"
    os.makedirs(folder_name, exist_ok=True)
    filename = os.path.join(folder_name, f'dns_results_{timestamp}.csv')

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Subdomain', 'Result'])
        writer.writerows(results)

    print(f"DNS requests completed and written to {filename}")

if __name__ == "__main__":
    main()