import yaml


class ConfigYaml:
    config_yaml = "config.yaml"

    def __init__(self, base_path):
        try:
            self.config_file_path = f"{base_path}/{self.config_yaml}"
            with open(self.config_file_path) as f:
                self.propertities = yaml.load(f, Loader=yaml.FullLoader)
        except:
            raise Exception(f"{self.config_yaml}파일이 존재하지 않습니다.")

    def get_propertity(self, propertity: str):

        if propertity in self.propertities:
            return self.propertities[propertity]

        raise KeyError(f"config_yaml에 {propertity} 가 존재하지 않습니다.")
