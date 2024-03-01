import csv
import geoip2.database
import sys
import os

# Check for command-line arguments
if len(sys.argv) != 3:
    sys.exit("Usage: script.py input_csv_path output_csv_path")

# Paths to the databases
db_path_city = 'db/GeoLite2-City.mmdb'  # Update this path
db_path_asn = 'db/GeoLite2-ASN.mmdb'  # Update this path

# Paths from command-line arguments
input_csv_path = sys.argv[1]
output_csv_path = sys.argv[2]

# Generate the second output file path
output_csv_path_no_ips = os.path.splitext(output_csv_path)[0] + "_no_ips.csv"
def read_ips_from_csv(input_csv_path):
    with open(input_csv_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        return [row for row in reader]

def lookup_ip_addresses(ip_records, output_csv_path, output_csv_path_no_ips):
    with geoip2.database.Reader(db_path_city) as city_reader, \
         geoip2.database.Reader(db_path_asn) as asn_reader, \
         open(output_csv_path, mode='w', newline='') as csv_file, \
         open('webserver/output.csv', mode='w', newline='') as webserver_csv_file, \
         open(output_csv_path_no_ips, mode='w', newline='') as csv_file_no_ips:
        
        fieldnames = ['ip', 'country', 'city', 'lat', 'long', 'ASN', 'ISP', 'moniker', 'version']
        fieldnames_no_ips = ['country', 'city', 'lat', 'long', 'ASN', 'ISP', 'moniker', 'version']
        
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        webserver_writer = csv.DictWriter(webserver_csv_file, fieldnames=fieldnames)  # Correct file object
        writer_no_ips = csv.DictWriter(csv_file_no_ips, fieldnames=fieldnames_no_ips)
        
        writer.writeheader()
        webserver_writer.writeheader()  # Correct writer
        writer_no_ips.writeheader()
        
        for record in ip_records:
            ip = record['ip']
            try:
                response_city = city_reader.city(ip)
                response_asn = asn_reader.asn(ip)
                
                row_data = {
                    'ip': ip,
                    'country': response_city.country.name,
                    'city': response_city.city.name,
                    'lat': response_city.location.latitude,
                    'long': response_city.location.longitude,
                    'ASN': response_asn.autonomous_system_number,
                    'ISP': response_asn.autonomous_system_organization,
                    'moniker': record['moniker'],
                    'version': record['version']
                }
                
                writer.writerow(row_data)
                webserver_writer.writerow(row_data)
                # Exclude 'ip' field for the second file
                row_data_no_ips = row_data.copy()
                del row_data_no_ips['ip']
                writer_no_ips.writerow(row_data_no_ips)
                
            except geoip2.errors.AddressNotFoundError:
                print(f"IP: {ip} - Address not found.")
            except Exception as e:
                print(f"Error retrieving information for IP: {ip}, Error: {e}")

ip_records = read_ips_from_csv(input_csv_path)
lookup_ip_addresses(ip_records, output_csv_path, output_csv_path_no_ips)
