import csv
import dns.resolver
import concurrent.futures
from datetime import datetime
import threading
import time
import queue

def dns_lookup(subdomains, resolver, completed_tasks_queue):
    results = []
    for subdomain in subdomains:
        try:
            answers = resolver.resolve(subdomain, 'A')
            for answer in answers:
                if str(answer) != "NXDOMAIN":
                    results.append([subdomain, str(answer)])
        except dns.resolver.NXDOMAIN:
            pass
        except (dns.resolver.NoAnswer, dns.resolver.Timeout, dns.resolver.NoNameservers):
            pass
        except Exception as e:
            results.append([subdomain, f"Error: {str(e)}"])

        # Mark the task as completed
        completed_tasks_queue.put(None)

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

def monitor_progress(total_tasks, completed_tasks_queue):
    while True:
        completed_tasks_count = completed_tasks_queue.qsize()
        progress = (completed_tasks_count / total_tasks) * 100
        print(f"Progress: {progress:.2f}%", end='\r')
        if completed_tasks_count >= total_tasks:
            break
        time.sleep(1)

def main():
    characters = "abcdefghijklmnopqrstuvwxyz0123456789" # Add more characters if needed

    num_characters = int(input("Enter the number of characters for subdomains: "))
    subdomains = generate_subdomains(characters, num_characters)

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['1.1.1.1']  # Use local DNS server at IP 192.168.11.5

    completed_tasks_queue = queue.Queue()
    total_tasks = len(subdomains)

    # Start the progress monitor thread
    progress_thread = threading.Thread(target=monitor_progress, args=(total_tasks, completed_tasks_queue), daemon=True)
    progress_thread.start()

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Split subdomains into chunks to distribute across threads
        chunk_size = 100
        subdomain_chunks = [subdomains[i:i+chunk_size] for i in range(0, len(subdomains), chunk_size)]

        # Submit each subdomain chunk to the executor
        future_to_chunk = {executor.submit(dns_lookup, chunk, resolver, completed_tasks_queue): chunk for chunk in subdomain_chunks}
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk = future_to_chunk[future]
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"Error processing chunk: {e}")

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
