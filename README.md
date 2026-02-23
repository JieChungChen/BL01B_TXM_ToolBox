# BL01B TXM ToolBox

A PyQt5-based GUI application for Transmission X-ray Microscopy (TXM) data processing and analysis.

## Features

### Data Loading
- **Tomography TXRM Files**: Load single or multiple `.txrm` files for tomographic reconstruction
- **Mosaic XRM Files**: Load `.xrm` files for mosaic stitching
- **Single XRM Files**: Load single `.xrm` files
- **TIF Image Folders**: Import existing TIF image sequences

### Image Processing
- **Reference Correction**: Apply reference images for flat-field correction (supports Single and Dual reference modes)
- **Contrast Adjustment**: Real-time contrast adjustment with clipping control
- **Vertical Flip**: Flip images along the vertical axis
- **Y-Shift**: Shift images vertically

### Tomography Features
- **Manual Alignment**: Interactive alignment tool with Tomography, Horizontal Sum, and Sinogram views
- **Auto Alignment**: Cross-correlation based auto-alignment using Horizontal Sum
- **FBP Reconstruction**: Filtered Back Projection reconstruction with resolution selection and optional ASTRA GPU acceleration
- **Duplicate Angle Handling**: Resolve duplicate angles when loading multiple TXRM files

### Mosaic Features
- **Mosaic Stitching**: Automatic stitching of mosaic tiles
- **Full View Preview**: Preview and save stitched mosaic images

### Exporting
- **Save Raw**: Save images as raw TIF files
- **Save Normalized**: Save images as normalized 8-bit TIF files

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
cd BL01B_TXM_ToolBox
python app.py
```

### Package as Executable
```bash
pyinstaller --onefile --noconsole --icon=tests/txm_icon_v2.png --name=TXM_ToolBox app.py
```

### Loading Data
1. **File Menu**:
   - `Tomography > Load TXRM`: Load single tomography file
   - `Tomography > Load Multiple TXRM`: Load and merge multiple tomography files
   - `Tomography > Load TIFs`: Load TIF image folder
   - `Mosaic > Load XRM`: Load mosaic file
   - `Mosaic > Load TIFs`: Load mosaic TIF folder
   - `Single > Load XRM`: Load single XRM file

### Image Processing
1. **Process Menu**:
   - `Load Reference`: Apply reference image for flat-field correction (Single or Dual mode)
   - `Adjust Contrast`: Open contrast adjustment dialog
   - `Vertical Flip`: Flip images vertically
   - `Y-Shift`: Shift images vertically

### Tomography Tools
1. **Alignment**:
   - `Tools > Manual Alignment`: Open alignment viewer
   - Use WASD keys to shift images
   - Doubleclick on image to center on that point
   - Use `HS Align` for cross-correlation auto-alignment
   - View Horizontal Sum and Sinogram for alignment feedback
   - Save/Load alignment shifts

2. **Reconstruction**:
   - `Tools > FBP Reconstruction`: Run filtered back projection
   - Select target resolution and angle interval
   - View reconstructed slices with slider

### Mosaic Tools
1. **Stitching**:
   - `Tools > Full View`: Preview stitched mosaic
   - Adjust contrast and save result

### Exporting
1. **File Menu**:
   - `Save > Save Raw`: Save images as raw TIF files
   - `Save > Save Normalized`: Save images as normalized 8-bit TIF files

## Project Structure
```
BL01B_TXM_ToolBox/
├── app.py                          # Main application entry
├── requirement.txt                 # Python dependencies
├── src/
│   ├── gui/                        # GUI components
│   │   ├── main_window.py          # Main window UI
│   │   ├── manual_alignment.py     # Alignment tool
│   │   ├── cc_align_dialog.py      # Cross-correlation auto-alignment
│   │   ├── contrast_dialog.py      # Contrast adjustment
│   │   ├── fbp_viewer.py           # FBP result viewer
│   │   ├── mosaic_viewer.py        # Mosaic preview
│   │   ├── reference_dialog.py     # Reference mode selection
│   │   ├── yshift_dialog.py        # Y-axis shift dialog
│   │   └── duplicates_selector.py  # Duplicate angle resolver
│   └── logic/                      # Core logic
│       ├── app_context.py          # Application state management
│       ├── data_io.py              # File I/O operations
│       ├── image_container.py      # Image data model
│       ├── fbp.py                  # FBP reconstruction
│       ├── decorators.py           # Error handling decorators
│       ├── exceptions.py           # Custom exceptions
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
- `Zoom In/Out`: Adjust view scale
- `Change Center`: Modify rotational center
- `Zoom Tomo`: Toggle zoomed view of tomography
- `Reset Sino`: Reset sinogram view

## Version History

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Developed for BL01B beamline at NSRRC (National Synchrotron Radiation Research Center)
