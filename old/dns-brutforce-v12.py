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
                results.append([subdomain, str(answer)])
        except Exception as e:
            results.append([subdomain, f"Error: {str(e)}"])
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
            subdomains.add(subdomain)
    return [subdomain + '.mr-joep.nl' for subdomain in subdomains]

def main():
    characters = "abcdefghijklmnopqrstuvwxyz0123456789-"
    max_length = int(input("Enter the maximum length of subdomains: "))

    subdomains = generate_subdomains(characters, max_length)

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['192.168.11.5']  # Use local DNS server at IP 192.168.11.5

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        chunk_size = 100
        subdomain_chunks = [subdomains[i:i+chunk_size] for i in range(0, len(subdomains), chunk_size)]

        future_to_chunk = {executor.submit(dns_lookup, chunk, resolver): chunk for chunk in subdomain_chunks}
        for future in concurrent.futures.as_completed(future_to_chunk):
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"Error processing chunk: {e}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("raw", f'dns_results_{timestamp}.csv')

    os.makedirs("raw", exist_ok=True)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Subdomain', 'Result'])
        writer.writerows(results)

    print(f"DNS requests completed and written to {filename}")

if __name__ == "__main__":
    main()
