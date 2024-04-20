import csv
import dns.resolver
import time
from datetime import datetime

def dns_lookup(subdomains, resolver):
    results = []
    total_subdomains = len(subdomains)
    for i, subdomain in enumerate(subdomains, start=1):
        try:
            answers = resolver.resolve(subdomain, 'A')
            for answer in answers:
                results.append([subdomain, str(answer)])
        except dns.resolver.NXDOMAIN:
            results.append([subdomain, "NXDOMAIN"])
        except dns.resolver.NoAnswer:
            results.append([subdomain, "NoAnswer"])
        except dns.resolver.Timeout:
            results.append([subdomain, "Timeout"])
        except dns.resolver.NoNameservers:
            results.append([subdomain, "NoNameservers"])
        except Exception as e:
            results.append([subdomain, f"Error: {str(e)}"])
        # Calculate progress and print it
        progress = i / total_subdomains * 100
        print(f"Progress: {progress:.2f}% ({i}/{total_subdomains})", end='\r')
    print()  # Move to the next line after progress is complete
    return results

def generate_subdomains(characters, num_characters):
    subdomains = []
    for char in characters:
        subdomains.append(char)
    for _ in range(num_characters - 1):
        new_subdomains = []
        for subdomain in subdomains:
            for char in characters:
                new_subdomains.append(subdomain + char)
        subdomains = new_subdomains
    return [subdomain + '.mhao888.com' for subdomain in subdomains]

def main():
    characters = "abcdefghijklmnopqrstuvwxyz0123456789" # Add more characters if needed

    num_characters = int(input("Enter the number of characters for subdomains: "))
    subdomains = generate_subdomains(characters, num_characters)

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['1.1.1.1']  # Use local DNS server at IP 192.168.11.5

    while True:
        results = dns_lookup(subdomains, resolver)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'dns_results_{timestamp}.csv'

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Subdomain', 'Result'])
            writer.writerows(results)

        print(f"DNS requests completed and written to {filename}")

        time.sleep(1)

if __name__ == "__main__":
    main()
