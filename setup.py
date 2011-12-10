from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='foodoverip',
      version=version,
      description="foodoverip",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='food over ip',
      author='Gevrey-Chambertin Crew',
      author_email='',
      url='http://foodoverip.org',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'pyramid',
          'pyramid_debugtoolbar',
          'velruse',
          'tweepy',
          'redis',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = foodoverip:main
      """,
      paster_plugins=['pyramid'],
      )
