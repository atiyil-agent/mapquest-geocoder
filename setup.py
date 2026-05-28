from setuptools import setup, find_packages

setup(
    name='mapquest_geocoder',
    version='0.1.0',
    description='A command-line tool to retrieve latitude and longitude using the MapQuest Geocoding API',
    author='Atilay Yilmaz',
    author_email='atiyil@gmail.com',
    url='https://github.com/atiyil/mapquest-geocoder',
    packages=find_packages(),
    install_requires=[
        'requests>=2.20.0',
    ],
    entry_points={
        'console_scripts': [
            'mapquest-geocode=mapquest_geocoder.geocode:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
