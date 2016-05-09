from setuptools import setup

setup(name='stipythonws',
      version='0.1',
      description='STI Websockets adapter for Python',
      author='MikeS',
      author_email='mike@sportshubtech',
      license='Proprietary',
      packages=['stipythonws'],
      install_requires=[
        'redis',
        'tornado'
      ],
      zip_safe=False)
