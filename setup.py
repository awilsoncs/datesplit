from distutils.core import setup

setup(name='datesplit',
	version='0.1',
	description='Split dates in CVS files.',
	author='Aaron Wilson',
	console=['datesplit.py'],
	install_requires=['gooey', 'dateparser']
	)
