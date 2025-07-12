from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="modeless-pose-estimation",
    version="1.0.0",
    author="Mukesh Odeti",
    author_email="mukesh.odeti@example.com",
    description="A lightweight, real-time 6D pose estimation pipeline using HSV color segmentation and 3D geometry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/omukesh/Pose_estimate_color_object_geometry",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Computer Vision",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
        ],
        "docs": [
            "sphinx>=7.1.2",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pose-estimation=6D_pose_color:main",
            "calibrate-camera=calibration_charuco:main",
            "generate-charuco=charuco_generate:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.png", "*.jpg", "*.npz"],
    },
    keywords="computer-vision pose-estimation opencv realsense robotics",
    project_urls={
        "Bug Reports": "https://github.com/omukesh/Pose_estimate_color_object_geometry/issues",
        "Source": "https://github.com/omukesh/Pose_estimate_color_object_geometry",
        "Documentation": "https://github.com/omukesh/Pose_estimate_color_object_geometry#readme",
    },
) 