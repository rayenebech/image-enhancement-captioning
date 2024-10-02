import yaml
import re

def read_config(config_path ="config.yaml"):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        return config
    
def singleton(cls):
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

def parse_data(data):
    parsed_data = {}
    try:
        for line in data.strip().split('\n'):
            splitted = line.split(">:")
            key = splitted[0].split("<")[-1]
            value = splitted[-1]
            parsed_data[key.strip()] = value.strip()

        return parsed_data
    
    except Exception as e:
        print("Error when parsing the data: ", e)
        return data
  
if __name__ == "__main__":
    text = """* <entity_name>: syrup
* <product_title>: Zühre Ana Karadut Özü - Black Mulberry Extract
* <product_description>: %100 doğal karadut özü. Taze ve doğal karadutun tüm lezzetini ve besleyici değerlerini barındıran Zühre Ana Karadut Özü'nü kuru bir yerde saklayın."""
    data = parse_data(text)
    print(data)