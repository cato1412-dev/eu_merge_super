import os
import requests
import zipfile
import subprocess
import shutil

# 1. Tải file ZIP
def download_zip(url, output_path):
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"Tải file ZIP thành công: {output_path}")

# 2. Giải nén file ZIP
def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Giải nén file ZIP thành công: {extract_to}")

# 3. Gộp các file super.img.0, super.img.1, ...
def merge_super_img(image_dir, output_file):
    img_files = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.startswith('super.img.')])
    cmd = ['simg2img'] + img_files + [output_file]
    subprocess.run(cmd, check=True)
    print(f"Gộp các file super.img thành công: {output_file}")

    # Xóa các file super.img.0, super.img.1, ...
    for img_file in img_files:
        os.remove(img_file)
    print("Đã xóa các file super.img.0, super.img.1, ...")

# 4. Chỉnh sửa file .bat
def modify_bat_files(bat_files, image_dir):
    for bat_file in bat_files:
        with open(bat_file, 'r') as file:
            content = file.read()

        # Thay thế chuỗi cũ bằng chuỗi mới
        new_content = content.replace(
            '\n'.join([f'%fastboot% flash super {image_dir}/super.img.{i}' for i in range(14)]),
            '%fastboot% flash super images\\super.img'
        )

        with open(bat_file, 'w') as file:
            file.write(new_content)
        print(f"Đã chỉnh sửa file: {bat_file}")

# 5. Di chuyển super.img vào thư mục images và nén lại thành file ZIP mới
def repack_zip(extract_path, original_zip_name):
    new_zip_name = f"VieOS_{os.path.basename(original_zip_name)}"
    shutil.move(os.path.join(extract_path, 'super.img'), os.path.join(extract_path, 'images', 'super.img'))

    shutil.make_archive(new_zip_name.replace('.zip', ''), 'zip', extract_path)
    print(f"Đã nén lại thành file ZIP: {new_zip_name}")

# Đường dẫn và URL
zip_url = os.getenv('ZIP_URL')  # Lấy URL từ biến môi trường
zip_path = "/tmp/file.zip"
extract_path = "/tmp/extracted"
output_super_img = "/tmp/super.img"

# Thực hiện các bước
download_zip(zip_url, zip_path)
unzip_file(zip_path, extract_path)
merge_super_img(os.path.join(extract_path, 'images'), output_super_img)

# Tìm và chỉnh sửa các file .bat
bat_files = [
    os.path.join(extract_path, 'windows_fastboot_first_install_with_data_format.bat'),
    os.path.join(extract_path, 'windows_fastboot_update_rom.bat')
]
modify_bat_files(bat_files, 'images')

# Di chuyển super.img vào thư mục images và nén lại thành file ZIP mới
repack_zip(extract_path, zip_path)
