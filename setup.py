from setuptools import setup, find_packages

setup(name='acc_api',
      version='0.0.dev0',
      description=('acc json API layer'),
      author='Adi Saric',
      author_email='adi@auset.net.au',
      license='Copyright (C) Ergon Energy, Inc - All Rights Reserved',
      packages=find_packages(),
      scripts=[
            'scripts/apifast.py'
      ],
      install_requires=[

            'xmltodict',
            'fastapi',
            'uvicorn',
            'starlette_exporter',
            'pyasn1',
            'pyasn1_modules',
            'requests',
            'fastapi_utils'
      ],
      zip_safe=True)