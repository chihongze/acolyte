import setuptools
from acolyte import VERSION

install_requires = [
    "tornado >= 4.4.0",
    "simplejson >= 3.8.2",
    "PyMySQL >= 0.7.9",
    "fixtures >= 3.0.0",
    "termcolor >= 1.1.0",
]

setuptools.setup(
    name="Acolyte",
    version=VERSION,
    author="ChiHongze",
    author_email="chihz@easemob.com",
    url='http://github.com/chihongze/easemob-flow',
    description=(
        "An interactive flow framework, you can use it to build "
        "CI, CD system"
    ),
    license="MIT",
    packages=setuptools.find_packages("."),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [

        ],
        "acolyte.job": [
            "programmer = acolyte.builtin_ext.mooncake:ProgrammerJob",
            "hr = acolyte.builtin_ext.mooncake:HRJob",
            "boss = acolyte.builtin_ext.mooncake:BossJob"
        ],
        "acolyte.flow_meta": [
            "mooncake_flow = acolyte.builtin_ext.mooncake:MooncakeFlowMeta"
        ]
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
