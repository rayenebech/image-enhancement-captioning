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

def load_yaml_data(text):
    text = text.strip("```yaml")
    text = text.replace("```", "")
    try:
        data = yaml.safe_load(text)
        print("data from yaml", data)
        return data
    except Exception as e:
        print("Error when loading yaml", e)
        return text
    
    
def parse_product_info(output_text):
    if output_text.strip().startswith("```yaml"):
        data = load_yaml_data(output_text)
        if isinstance(data, dict):
            return data
    lines = output_text.splitlines()
    parsed_info = {}
    for line in lines:
        if "entity_name" in line:
            parsed_info['entity_name'] = line.split("entity_name")[1].strip(":").strip()
        elif "product_title" in line:
            parsed_info['product_title'] = line.split("product_title")[1].strip(":").strip()
        elif "product_description" in line:
            parsed_info['product_description'] = line.split("product_description:")[1].strip(":").strip()
    return parsed_info

if __name__ == "__main__":
    text = """```yaml
  entity_name: jar
  product_title: 100 Ganik Doğal Kuşburnu Marmelatı - 700g
  product_description: 700 gramlık bu 100 doğal kuşburnu marmelatı, katkı maddesi içermez ve saf meyve lezzeti sunar.
  ```
  """
    data = parse_product_info(text)
    print(data)