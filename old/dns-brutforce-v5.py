import csv
import dns.resolver
import concurrent.futures
from datetime import datetime
import threading
import time

def dns_lookup(subdomains, resolver, completed_tasks):
    results = []
    total_subdomains = len(subdomains)
    for i, subdomain in enumerate(subdomains, start=1):
        try:
            answers = resolver.resolve(subdomain, 'A')
            for answer in answers:
                if str(answer) != "NXDOMAIN":
                    results.append([subdomain, str(answer)])
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.NoAnswer:
            results.append([subdomain, "NoAnswer"])
        except dns.resolver.Timeout:
            results.append([subdomain, "Timeout"])
        except dns.resolver.NoNameservers:
            results.append([subdomain, "NoNameservers"])
        except Exception as e:
            results.append([subdomain, f"Error: {str(e)}"])
        # Calculate progress and print it
        completed_tasks.append(i)
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
    return [subdomain + '.mr-joep.nl' for subdomain in subdomains]

def monitor_progress(total_tasks, completed_tasks):
    while len(completed_tasks) < total_tasks:
        progress = len(completed_tasks) / total_tasks * 100
        print(f"Progress: {progress:.2f}%", end='\r')
        time.sleep(1)

def main():
    characters = "abcdefghijklmnopqrstuvwxyz0123456789" # Add more characters if needed

    num_characters = int(input("Enter the number of characters for subdomains: "))
    subdomains = generate_subdomains(characters, num_characters)

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['192.168.11.5']  # Use local DNS server at IP 192.168.11.5

    completed_tasks = []
    total_tasks = len(subdomains)

    # Start the progress monitor thread
    progress_thread = threading.Thread(target=monitor_progress, args=(total_tasks, completed_tasks), daemon=True)
    progress_thread.start()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Split subdomains into chunks to distribute across threads
        chunk_size = 200
        subdomain_chunks = [subdomains[i:i+chunk_size] for i in range(0, len(subdomains), chunk_size)]

        results = []
        for result_chunk in executor.map(lambda chunk: dns_lookup(chunk, resolver, completed_tasks), subdomain_chunks):
            results.extend(result_chunk)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'dns_results_{timestamp}.csv'

    # Filter out responses containing "NXDOMAIN"
    results = [result for result in results if "NXDOMAIN" not in result]

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Subdomain', 'Result'])
        writer.writerows(results)

    print(f"DNS requests completed and written to {filename}")
    print("Progress: 100.00%")

if __name__ == "__main__":
    main()
