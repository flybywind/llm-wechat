from setuptools import setup

APP = ['main.py']
DATA_FILES = []
# 读取 requirements.txt 文件
def read_requirements(file_path):
    with open(file_path) as file:
        lines = file.readlines()
    # 去除注释和空行
    requirements = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return requirements

INSTALL_REQUIRES = read_requirements('requirements.txt')

OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True
        }
    },
    'packages': ['myconf'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    python_requires='>=3.11, <4.0',  # 指定 Python 版本
    install_requires=INSTALL_REQUIRES,
)