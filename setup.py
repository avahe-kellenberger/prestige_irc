from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="prestige_irc",
    version="0.0.4",
    author="Avahe Kellenberger",
    author_email="avahe@protonmail.ch",
    description="A simple API for IRC networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avahe-kellenberger/prestige_irc",
    packages=["prestige_irc"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent"
    ]
)
