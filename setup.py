import setuptools
from easemob_flow import VERSION

install_requires = [
    "flask >= 0.11",
    "ujson >= 1.35",
    "PyMySQL >= 0.7.9",
    "fixtures >= 3.0.0",
]

setuptools.setup(
    name="easemob-flow",
    version=VERSION,
    author="ChiHongze",
    author_email="chihz@easemob.com",
    url='http://github.com/chihongze/easemob-flow',
    description=(
        ""
    ),
    license="MIT",
    packages=setuptools.find_packages("."),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [

        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5'
    ]
)
