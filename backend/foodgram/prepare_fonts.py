"""
Script to download DejaVuSans font for PDF generation.
Run this script before starting the application.
"""

import os
import urllib.request
import tempfile
import zipfile
import shutil


def download_dejavu_sans():
    """Download the DejaVuSans.ttf font if it doesn't exist."""
    font_dir = 'fonts'
    font_path = os.path.join(font_dir, 'DejaVuSans.ttf')

    if not os.path.exists(font_dir):
        os.makedirs(font_dir)

    if not os.path.exists(font_path):
        print('Downloading DejaVuSans.ttf font...')
        url = 'https://dejavu-fonts.github.io/Files/dejavu-sans-ttf-2.37.zip'

        try:
            with tempfile.NamedTemporaryFile(suffix='.zip',
                                             delete=False) as temp_file:
                urllib.request.urlretrieve(url, temp_file.name)

                with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
                    font_file_in_zip = None
                    for file_name in zip_ref.namelist():
                        if file_name.endswith('DejaVuSans.ttf'):
                            font_file_in_zip = file_name
                            break

                    if font_file_in_zip:
                        with zip_ref.open(font_file_in_zip) as source_file, \
                             open(font_path, 'wb') as target_file:
                            target_file.write(source_file.read())
                    else:
                        print("Шрифт DejaVuSans.ttf не найден в архиве")

                os.unlink(temp_file.name)

            print(f'Font downloaded and extracted to {font_path}')
        except Exception as e:
            print(f"Ошибка при загрузке шрифта: {e}")
            fallback_font_path = (
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
            )
            if os.path.exists(fallback_font_path):
                shutil.copy(fallback_font_path, font_path)
                print(f'Used system font instead: {font_path}')
    else:
        print(f'Font already exists at {font_path}')


if __name__ == '__main__':
    download_dejavu_sans()
