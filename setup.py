from setuptools import setup, find_packages

setup(
    name='medbot-healthcare',
    version='1.0.0',
    description='A Flask-based Medical Question Answering Bot',
    author='CALEB UNIVERSITY BUESA REPRESENTATIVE',
    url='https://github.com/abu-muhammedx7/medbot-healthcare',
    packages=find_packages(),
    include_package_data=True,  # includes static, templates, etc.
    install_requires=[
        'Flask>=2.0.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Flask',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'medbot=app:app',
        ],
    },
)
