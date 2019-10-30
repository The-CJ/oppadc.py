import setuptools, re, pathlib
here = pathlib.Path(__file__).parent

with open(f"{here}/README.md", "r") as rm:
	long_description = rm.read()

requirements = []
with open(f"{here}/requirements.txt", "r") as req:
  requirements = req.read().splitlines()

try:
	version = re.findall(r"^__version__\s?=\s?[\'\"](.+)[\'\"]$", open("oppadc/__init__.py").read(), re.M)[0]
except IndexError:
	raise RuntimeError('Unable to determine version.')

setuptools.setup(
	name="oppadc",
	version=version,
	author="The_CJ",
	author_email="dev@phaaze.net",
	description="osu! performance points and difficulty calculator",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/The-CJ/oppadc.py",
	license="MIT",
	install_requires=requirements,
	packages=["oppadc"],
	classifiers=[
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent"
	],
)
