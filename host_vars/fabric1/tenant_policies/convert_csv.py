import csv
import yaml

csv_file = 'tn-bd.csv'
yaml_file = 'bd_convert.yml'

boolean_fields = [
    'enable_routing',
    'ip_learning',
    'enable_multicast',
    'arp_flooding',
]

integer_fields = ['mask']

with open(csv_file, newline='') as f:
    reader = csv.DictReader(f)
    data = []
    for row in reader:
        for field in boolean_fields:
            if field in row:
                val = row[field].strip().lower()
                print(f"Normalizing {field}: '{row[field]}' → '{val}'")  # Debug line
                if val == 'true':
                    row[field] = True
                elif val == 'false':
                    row[field] = False

        for field in integer_fields:
            if field in row:
                try:
                    row[field] = int(row[field])
                except ValueError:
                    pass

        data.append(row)

output_data = {'bridge_domains' : data}

with open(yaml_file, 'w') as f:
    yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)