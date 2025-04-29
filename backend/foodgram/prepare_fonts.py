#!/usr/bin/env python
"""
Script to download DejaVuSans font for PDF generation.
Run this script before starting the application.
"""
import os
import urllib.request


def download_dejavu_sans():
    """Download the DejaVuSans.ttf font if it doesn't exist."""
    font_dir = 'fonts'
    font_path = os.path.join(font_dir, 'DejaVuSans.ttf')
    
    if not os.path.exists(font_dir):
        os.makedirs(font_dir)
    
    if not os.path.exists(font_path):
        print('Downloading DejaVuSans.ttf font...')
        url = 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf'
        urllib.request.urlretrieve(url, font_path)
        print(f'Font downloaded to {font_path}')
    else:
        print(f'Font already exists at {font_path}')


if __name__ == '__main__':
    download_dejavu_sans() 