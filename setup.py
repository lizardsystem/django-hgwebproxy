from setuptools import setup

version = '0.3.dev0'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
])

install_requires = [
    'Django',
    'South',
    'mercurial',
],

tests_require = [
    'nose',
    'coverage',
    'mock',
    'factory_boy',
]

setup(name='django-hgwebproxy',
      version=version,
      description=("django-hgwebproxy is a django application which provides "
                   "a django version of mercurials hgwebdir interface."),
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Sander Smits',
      author_email='sander.smits@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['hgwebproxy'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
          ]},
      )
