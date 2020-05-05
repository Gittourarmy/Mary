import os
import yaml
from pprint import pprint as pp

def init_language():
    """
    기본 언어 설정. 없으면 영어. 글-로벌
    """
    yaml_data = read_yaml("config.yaml", '!default')
    if yaml_data: return yaml_data.get('language') + "\\"
    else: return ""

def read_yaml(file, *args):
    """
    YAML 파일을 불러와 읽음. 번역 정보를 받음
    """

    print_info = True if 'info' in args else False
    default= False if '!default' in args else True

    def set_file_path(file):
        FILE_PATH = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(FILE_PATH, file)

    if default:
        file = DEFAULT_FOLDER + LANG + file

    with open(set_file_path(file), 'r',  encoding='UTF8') as file:
        try:
            info = yaml.load(file, Loader=yaml.FullLoader)
            if print_info: pp(info)
            return info
        except yaml.YAMLError as exc:
            return exc

def cout(searching_object, *args):
    """
    원하는 yaml에서 추출한 객체를 이용해 메세지를 만들때 씀.
    args 쓰는 순서는 영어순대로, 번역파일에서 알아서 순서를 바꾸니 다르게 할 필요는 없음
    """
    return searching_object['log_format'].format(*args)

DEFAULT_FOLDER = "translations\\"
LANG = init_language()
SYS_LOG = read_yaml("system_log.yaml")

if __name__ == "__main__":
    artifacts = read_yaml("artifacts.yaml")
    talisman = artifacts['talisman']
    log = talisman['quotes'][0]
    print(cout(talisman, talisman['effect_log'], log))