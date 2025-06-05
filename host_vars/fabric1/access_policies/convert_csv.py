import csv
import yaml

csv_file = 'ap-aaeps.csv'
yaml_file = 'aaeps_convert.yml'

with open(csv_file, newline='') as f:
    reader = csv.DictReader(f)
    data = []
    for row in reader:
        data.append(row)

output_data = {'aaeps' : data}

with open(yaml_file, 'w') as f:
    yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)