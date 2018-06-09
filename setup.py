from setuptools import setup

setup(
    name="tested_deployments",
    version="0.3.0",
    author="D. Scott Boggs",
    author_email="scott@tams.tech",
    url="https://github.com/dscottboggs/Deployments",
    description="Containerized tested (pytest) and secured (LetsEncrypt) deployments.",
    classifiers=[
        "Environment :: Web Environment",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English ",
        "Operating System :: POSIX :: Linux",
        "Topic :: Internet :: WWW/HTTP"
    ],
    modules=[
        "deployments.reverse_proxy",
        "deployments.resume",
        "deployments.nextcloud"
    ],
    install_requires=[
        'docker', 'pytest', 'PyYaml', 'Jinja2', 'requests'
    ]
)
