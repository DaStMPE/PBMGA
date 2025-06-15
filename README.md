# PBMGA (Python Bone Material Grouping and Anisotropy)

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.XXXX/XXXXX-blue)](https://doi.org/10.XXXX/XXXXX)

A Python tool for processing and enhancing CT-mapped material properties in bone finite element analysis, with support for non-linear and anisotropic material models.

> ⚠️ **IMPORTANT DISCLAIMER**: This software is intended for research purposes only. It is not approved for clinical use and should not be used for diagnostic or therapeutic purposes. The results obtained from this software should be validated through appropriate research protocols and should not be used to make clinical decisions.

## 📋 Overview

PBMGA is designed to streamline the implementation of non-linear and anisotropic material models for CT-mapped material properties in bone finite element analysis. This tool bridges the gap between CT scan data and advanced material modeling in Abaqus, eliminating the need for manual property assignment.

### Key Features
- Multiple material grouping methods for bone tissue classification
- Support for non-linear material behavior
- Implementation of anisotropic material properties
- Direct integration with Bonemat-generated INP files
- Preprocessing tools for non-Bonemat meshes
- Compatible with Abaqus finite element analysis

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- Abaqus (for FE analysis)
- Bonemat V3.2 (optional, for initial material mapping)

### Installation Steps
1. Clone the repository:
```bash
git clone https://github.com/yourusername/PBMGA.git
cd PBMGA
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Configuration
1. Configure your settings in `config.py` in the main directory. Here are the main configuration options:

```python
# Directory and file settings
directory = ''  # Path to your working directory
file_name1 = ''  # Name of your input file without extension
file_name = file_name1 + '.inp'  # Full input file name

# Grouping Method Options:
# - "Percentual_Thresholding"
# - "None" (no grouping)
# - "Kmeans_Clustering"
# - "Equidistant"
Grouping_Method = "Percentual_Thresholding"

# KMeans Clustering Options
plot_cluster_on = False  # Enable/disable cluster visualization
plot_percentual_diff_on = False  # Enable/disable difference visualization
num_clusters = 20  # Number of clusters for KMeans

# Threshold Options
threshold = 10  # Threshold percentage
threshold_percentage = threshold / 100

# Equidistant Grouping Options
num_equidistant_groups = 10  # Number of groups for equidistant grouping

# Material Configuration
class Material_Config:
    # Add your material property settings here
    # Example:
    Scale_E_x = 1.0  # Scaling factor for E_x
    Scale_E_y = 1.0  # Scaling factor for E_y
    Scale_G_xy = 1.0  # Scaling factor for G_xy
    Scale_G_xz = 1.0  # Scaling factor for G_xz
    Scale_G_yz = 1.0  # Scaling factor for G_yz
    Ass_V_xy = 0.3    # Assigned Poisson's ratio xy
    Ass_V_xz = 0.3    # Assigned Poisson's ratio xz
    Ass_V_yz = 0.3    # Assigned Poisson's ratio yz
```

### Running the Tool
1. For Bonemat V3.2 mapped meshes:
   - Configure `config.py` with your settings
   - Run the main script:
   ```bash
   python main.py
   ```

2. For other mesh formats:
   - Use the provided preprocessors in the `preprocessors/` directory
   - Available preprocessors:
     - `SimplewareScanIp/` - For SimpleWare ScanIP meshes
     - `Mimics/` - For Mimics meshes
     - `Bonemat4/` - For Bonemat4 Rolling version meshes
   - Configure the respective `config.py` in the preprocessor directory
   - Run the preprocessor
   - After preprocessing, configure and run the main script as above

## 📚 Material Grouping Methods

PBMGA supports multiple material grouping methods:

1. **Adaptive Clustering based on K-means Clustering**
   - Automatically groups bone tissue into distinct material groups
   - Configurable number of groups
   - Based on HU values and spatial distribution

2. **Equidistant Grouping**
   - Traditional approach using HU value thresholds
   - Similar to Mimics's and Simplewares grouping method
   - Customizable threshold values

3. **Percentual Thresholding**
   - Percentual Threshold between material bins



## 🔬 Scientific Background

This tool addresses the limitations of conventional bone material mapping tools (like Bonemat and SimpleWare ScanIP) by incorporating:
- Multiple material grouping strategies
- Anisotropic material behavior
- Non-linear material properties
- Advanced yield criteria
- Patient-specific material mapping

## 📝 Citation

If you use this software in your research, please cite:
TBD
```bibtex
@article{your_paper_2024,
    title={Your Paper Title},
    author={Your Name and Co-authors},
    journal={Journal Name},
    year={2024},
    doi={10.XXXX/XXXXX}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This research was supported by the Aarhus University Research Foundation under Grant Number: AUFF-E-2022-7-12.

## 📧 Contact

For questions and support, please contact:
- [Daniel Strack](mailto:dast@mpe.dk)
- [Project Issues](https://github.com/DaStMPE/PBMGA/issues)

## 🔄 Version History

- v1.0.0 (2025) - Initial release
  - Basic material property processing
  - Abaqus integration
  - Support for non-linear and anisotropic properties 