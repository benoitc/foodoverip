from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='foodoverip',
      version=version,
      description="foodoverip",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='food over ip',
      author='Gevrey-Chambertin-2009 Crew',
      author_email='',
      url='http://foodoverip.org',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'couchdbkit',
          'gevent',
          'pyquery',
          'PIL'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [console_scripts]
      go_grab_food = foodoverip.grabber:run
      make_food_thumb = foodoverip.make_thumb:run
      """)
