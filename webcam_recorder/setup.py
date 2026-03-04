from setuptools import find_packages, setup
package_name = 'webcam_recorder'
setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kenneth',
    maintainer_email='kenneth.eladistu@planate.com',
    description='Webcam publisher and bag recorder',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'webcam_node = webcam_recorder.webcam_node:main',
            'bag_recorder_node = webcam_recorder.bag_recorder_node:main',
            'language_publisher_node = webcam_recorder.language_publisher_node:main',
            'new_bag_recorder_node = webcam_recorder.new_bag_recorder_node:main',
        ],
    },
)
