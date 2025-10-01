# BL01B TXM ToolBox

A PyQt5-based GUI application for Transmission X-ray Microscopy (TXM) data processing and analysis.

## Features

### Data Loading
- **Tomography TXRM Files**: Load single or multiple `.txrm` files for tomographic reconstruction
- **Mosaic XRM Files**: Load `.xrm` files for mosaic stitching
- **TIF Image Folders**: Import existing TIF image sequences

### Image Processing
- **Reference Correction**: Apply reference images for flat-field correction
- **Contrast Adjustment**: Real-time contrast adjustment with clipping control
- **Vertical Flip**: Flip images along the vertical axis

### Tomography Features
- **Manual Alignment**: Interactive alignment tool with keyboard controls (WASD) and mouse-based positioning
- **FBP Reconstruction**: Filtered Back Projection reconstruction with Hann filter
- **Duplicate Angle Handling**: Resolve duplicate angles when loading multiple TXRM files

### Mosaic Features
- **Mosaic Stitching**: Automatic stitching of mosaic tiles
- **Full View Preview**: Preview and save stitched mosaic images

## Installation

### Prerequisites
- Python 3.8 or higher
- PyQt5
- NumPy
- Pillow
- olefile

### Install Dependencies
```bash
pip install -r requirement.txt
```

## Usage

### Run the Application
```bash
python app.py
```

### Loading Data
1. **File Menu**:
   - `Tomography > Load TXRM`: Load single tomography file
   - `Tomography > Load Multiple TXRM`: Load and merge multiple tomography files
   - `Tomography > Load TIFs`: Load TIF image folder
   - `Mosaic > Load XRM`: Load mosaic file
   - `Mosaic > Load TIFs`: Load mosaic TIF folder

### Image Processing
1. **Process Menu**:
   - `Load Reference`: Apply reference image for flat-field correction
   - `Adjust Contrast`: Open contrast adjustment dialog
   - `Vertical Flip`: Flip images vertically

### Tomography Tools
1. **Alignment**:
   - `Tools > Manual Alignment`: Open alignment viewer
   - Use WASD keys to shift images
   - Click on image to center on that point
   - Save/Load alignment shifts

2. **Reconstruction**:
   - `Tools > FBP Reconstruction`: Run filtered back projection
   - View reconstructed slices with slider

### Mosaic Tools
1. **Stitching**:
   - `Tools > Full View`: Preview stitched mosaic
   - Adjust contrast and save result

## Project Structure
```
BL01B_TXM_ToolBox/
├── app.py                          # Main application entry
├── requirement.txt                 # Python dependencies
├── src/
│   ├── gui/                        # GUI components
│   │   ├── main_window.py          # Main window UI
│   │   ├── manual_alignment.py     # Alignment tool
│   │   ├── contrast_dialog.py      # Contrast adjustment
│   │   ├── fbp_viewer.py           # FBP result viewer
│   │   ├── mosaic_preview.py       # Mosaic preview
│   │   └── integrate_multi_txrm.py # Duplicate angle resolver
│   └── logic/                      # Core logic
│       ├── data_io.py              # File I/O operations
│       ├── tomography.py           # Image data model
│       ├── fbp.py                  # FBP reconstruction
│       └── utils.py                # Utility functions
```

## Keyboard Shortcuts

### Alignment Viewer
- `W`: Shift image up
- `S`: Shift image down
- `A`: Shift image left
- `D`: Shift image right
- `Mouse Click`: Center image on clicked point
- `Drag Line`: Adjust reference line position

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Commit your changes with clear messages
4. Submit a pull request

## Version History

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Developed for BL01B beamline at NSRRC (National Synchrotron Radiation Research Center)
- Uses PyQt5 for GUI framework
- FBP reconstruction based on standard tomographic algorithms
