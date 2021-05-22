from setuptools import setup, find_packages

setup(name='pearson-api',
      version='1.1',
      description='Pearson API',
      author='Kacper Ziubryniewicz',
      author_email='kapi2289@gmail.com',
      url='https://github.com/kapi2289/pearson-api',
      packages=find_packages(),
      install_requires=['requests', 'beautifulsoup4']
)
