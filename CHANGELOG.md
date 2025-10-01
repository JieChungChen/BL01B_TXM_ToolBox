# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- Fixed undefined `dragging_line2` variable in manual_alignment.py

### Added
- Added requirement.txt with project dependencies
- Added .gitignore for Python projects
- Added README.md with comprehensive documentation
- Added CHANGELOG.md for version tracking

### Changed
- Cleaned up manual_alignment.py by removing unused line2 functionality

## [0.1.0] - Initial Version

### Features
- Load single/multiple TXRM files for tomography
- Load XRM files for mosaic imaging
- Load TIF image folders
- Reference image correction
- Contrast adjustment with live preview
- Manual alignment tool with WASD controls
- FBP reconstruction with Hann filter
- Mosaic stitching and preview
- Duplicate angle resolution for multi-file loading
- Save processed images as TIF sequences
