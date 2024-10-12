import os
import importlib

# 현재 파일의 디렉토리 경로를 얻음
package_dir = os.path.dirname(__file__)

# 디렉토리 내의 모든 .py 파일을 import
for filename in os.listdir(package_dir):
    if (
        filename.endswith(".py")
        and filename != "__init__.py"
        and filename != "base_router.py"
    ):
        module_name = filename[:-3]
        importlib.import_module(f".{module_name}", package=__name__)
