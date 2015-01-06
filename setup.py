from distutils.core import setup
import os, sys

pkgname = "SHARPpy"
setup_path = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(os.path.join(setup_path, pkgname.lower()))
import version
version.write_git_version()
ver = version.get_version()
sys.path.pop()


setup(
    name = pkgname,
    version = ver,
    author = "Patrick Marsh, John Hart, Kelton Halbert, and Greg Blumberg",
    author_email = "patrick.marsh@noaa.gov, john.hart@noaa.gov, keltonhalbert@ou.edu, wblumberg@ou.edu",
    description = ("Sounding/Hodograph Analysis and Research Program " \
        "for Python"),
    license = "BSD",
    keywords = "meteorology soundings analysis",
    url = "",
    packages=['sharppy', 'sharppy.io', 'sharppy.sharptab', 'sharppy.viz', 'sharppy.databases'],
    package_data={'': ['*.md', '*.txt', '*.png']},
    include_package_data=True,
    long_description="",
    classifiers=["Development Status :: 2 - Pre-Alpha"],
)
