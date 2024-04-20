import csv
import dns.resolver
import concurrent.futures
from datetime import datetime
import os

def dns_lookup(subdomains, resolver, completed_tasks_queue):
    results = []
    for subdomain in subdomains:
        try:
            answers = resolver.resolve(subdomain, 'A')
            for answer in answers:
                if str(answer) != "NXDOMAIN":
                    results.append([subdomain, str(answer)])
        except:
            pass

        # Mark the task as completed
        completed_tasks_queue.put(None)

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
            subdomains.add(subdomain + '.mr-joep.nl')
    return list(subdomains)

def monitor_progress(total_tasks, completed_tasks_queue):
    while True:
        completed_tasks_count = completed_tasks_queue.qsize()
        progress = (completed_tasks_count / total_tasks) * 100
        print(f"Progress: {progress:.2f}%", end='\r')
        if completed_tasks_count >= total_tasks:
            break

def main():
    characters = "abcdefghijklmnopqrstuvwxyz0123456789-"
    max_length = int(input("Enter the maximum length of subdomains: "))

    subdomains = generate_subdomains(characters, max_length)

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['192.168.11.5']  # Use local DNS server at IP 192.168.11.5

    completed_tasks_queue = concurrent.futures.Queue()
    total_tasks = len(subdomains)

    # Start the progress monitor thread
    progress_thread = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    progress_thread.submit(monitor_progress, total_tasks, completed_tasks_queue)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_subdomain = {executor.submit(dns_lookup, [subdomain], resolver, completed_tasks_queue): subdomain for subdomain in subdomains}
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

    print(f"\nDNS requests completed and written to {filename}")

if __name__ == "__main__":
    main()
