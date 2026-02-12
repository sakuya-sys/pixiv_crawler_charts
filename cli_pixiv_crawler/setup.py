from setuptools import setup, find_packages

setup(
    name='pixiv_crawler',                     # 安装时的项目名
    version='1.0.0',
    description='Pixiv 图片下载命令行工具',
    packages=find_packages(),            # 自动包含 pixiv_download 包
    package_data={
        "pixiv_download":["config.yaml"]
    },
    install_requires=[
        'requests',                     # 依赖
    ],
    entry_points={
        'console_scripts': [
            'pixiv_crawler = pixiv_download.cli:cli',   # 假设你的 cli 在 main.py 中
        ],
    },
    python_requires='>=3.7',
)