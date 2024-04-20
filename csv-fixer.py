import os
import csv
import time

def get_last_csv_file(folder_path):
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    if not csv_files:
        return None
    return max(csv_files, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))

def sort_csv(input_file, output_file):
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the first row
        data = sorted(reader, key=lambda x: (len(x[0].split('.')[0]), x[0]))  # Sorting by gene length before ".", then alphabetically
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Create directory if it doesn't exist
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def main():
    raw_folder = "raw"
    good_folder = "good"
    
    while True:
        last_csv_file = get_last_csv_file(raw_folder)
        if last_csv_file:
            input_file = os.path.join(raw_folder, last_csv_file)
            output_file = os.path.join(good_folder, "sorted_" + last_csv_file)
            
            sort_csv(input_file, output_file)
            print(f"Sorted file saved to {output_file}")
        else:
            print("No CSV files found in the 'raw' folder.")
        
        time.sleep(10)  # Sleep for 10 seconds before checking again

if __name__ == "__main__":
    main()
