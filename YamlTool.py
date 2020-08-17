from ruamel import yaml

class Yaml_Tool:
    def __init__(self):
        pass

    def getParam(self, yamlPath):
        with open(yamlPath) as yamlFile:
            content = yaml.load(yamlFile, Loader=yaml.RoundTripLoader)
            yamlFile.close()
            return content

    def setValue(self, yamlPath, param, paramValue):
        with open(yamlPath, 'r') as yamlFile:
            content = yaml.safe_load(yamlFile)
            content[param] = paramValue
            yamlFile.close()

        with open(yamlPath, 'w') as yamlFile2:
            yaml.dump(content, yamlFile2, Dumper=yaml.RoundTripDumper)
            yamlFile2.close()

    def saveParam(self,yamlPath,param):
        with open(yamlPath, 'w') as yamlFile:
            yaml.dump(param, yamlFile, Dumper=yaml.RoundTripDumper)
            yamlFile.close()

if __name__ == '__main__':
    yamlTool=Yaml_Tool()
    print(yamlTool.getParam("configure.yaml")["Robot"]["robotFlag"])