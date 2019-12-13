from distutils.core import setup

setup(name='pearson-api',
      version='1.0',
      description='Pearson API',
      author='Kacper Ziubryniewicz',
      author_email='kapi2289@gmail.com',
      url='https://github.com/kapi2289/pearson-api',
      packages=['pearson'],
      requires=['requests', 'beautifulsoup4']
      )
