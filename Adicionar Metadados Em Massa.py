import subprocess
import sys
import time

# Lista de pacotes necessários
required_packages = [
    "Pillow",  # Para a biblioteca PIL (Pillow)
    "piexif",  # Para manipulação de metadados EXIF
]

def install_packages(packages):
    """Instala pacotes usando pip."""
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Instala os pacotes necessários
install_packages([pkg.split()[0] for pkg in required_packages])

from PIL import Image
import piexif
import os

def add_metadata_jpeg(image_path, description, subject, brands, lat=None, lon=None):
    """Adiciona metadados a um arquivo JPEG"""
    try:
        # Carrega os metadados existentes ou cria novos
        exif_dict = piexif.load(image_path)

        # Adiciona geolocalização, se disponível
        if lat is not None and lon is not None:
            gps_ifd = {
                piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
                piexif.GPSIFD.GPSLatitude: deg_to_dms_rational(abs(lat)),
                piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
                piexif.GPSIFD.GPSLongitude: deg_to_dms_rational(abs(lon)),
            }
            exif_dict['GPS'] = gps_ifd

        # Adiciona descrição, assunto e marcas nos campos apropriados
        zeroth_ifd = {
            piexif.ImageIFD.ImageDescription: description,
            piexif.ImageIFD.XPSubject: subject.encode('utf-16le'),
            piexif.ImageIFD.XPKeywords: brands.encode('utf-16le'),  # Usando XPKeywords para marcas
            piexif.ImageIFD.XPComment: brands.encode('utf-16le'),  # Alternativa para garantir visibilidade
        }

        # Atualiza os metadados
        exif_dict['0th'] = {**exif_dict.get('0th', {}), **zeroth_ifd}

        # Insere os metadados atualizados na imagem
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, image_path)

        print(f"Metadados adicionados com sucesso ao arquivo {image_path}")

    except Exception as e:
        print(f"Erro ao adicionar metadados ao arquivo JPEG: {e}")

def convert_to_rational(number):
    """Converte um número em uma tupla (numerador, denominador) para formato EXIF"""
    f = float(number)
    d = 1
    while not f.is_integer() and d <= 1000000:  # Limita o denominador a 1.000.000
        f *= 10
        d *= 10
    return int(f), d

def deg_to_dms_rational(deg):
    """Converte graus decimais para DMS (Degrees, Minutes, Seconds) no formato EXIF"""
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m/60) * 3600
    return (convert_to_rational(d), convert_to_rational(m), convert_to_rational(s))

def get_user_input(debug_mode=False):
    """Obtém informações do usuário ou usa valores padrão se em modo debug"""
    if debug_mode:
        # Valores padrão para modo debug
        description = "Descrição da Imagem"
        subject = "Assunto da Imagem"
        brands = "Marca1, Marca2, Marca3"
        latitude = -15.79285353301639
        longitude = -47.822122097923554
    else:
        # Coleta informações do usuário
        description = input("Digite a descrição da imagem: ")
        subject = input("Digite o assunto da imagem: ")
        brands = input("Digite as marcas / tags (separadas por vírgula): ")
        lat_lon = input("Digite a latitude e longitude separadas por vírgula (ex: -15.79285353301639, -47.822122097923554): ")
        latitude, longitude = map(float, lat_lon.split(','))

    return description, subject, brands, latitude, longitude

def convert_png_to_jpeg(png_path):
    """Converte um arquivo PNG para JPEG e retorna o caminho do novo arquivo"""
    try:
        # Abre o arquivo PNG
        with Image.open(png_path) as img:
            # Define o caminho do novo arquivo JPEG
            jpeg_path = png_path.rsplit('.', 1)[0] + '.jpg'
            # Converte para JPEG e salva
            img.convert('RGB').save(jpeg_path, 'JPEG')
            print(f"Arquivo convertido para JPEG: {jpeg_path}")
            return jpeg_path
    except Exception as e:
        print(f"Erro ao converter {png_path} para JPEG: {e}")
        return None

def process_images_in_directory(dir_path, description, subject, brands, lat=None, lon=None):
    """Processa todas as imagens JPEG em um diretório e adiciona metadados, além de converter PNGs para JPEG"""
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if filename.lower().endswith('.png'):
            # Converte PNG para JPEG e processa o novo arquivo
            jpeg_path = convert_png_to_jpeg(file_path)
            if jpeg_path:
                add_metadata_jpeg(jpeg_path, description, subject, brands, lat, lon)
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            # Processa arquivos JPEG diretamente
            add_metadata_jpeg(file_path, description, subject, brands, lat, lon)

# Modo debug (defina como True para usar valores padrão)
debug_mode = False

# Obtém as informações do usuário ou usa valores padrão
description, subject, brands, latitude, longitude = get_user_input(debug_mode)

# Diretório das imagens
dir_path = os.getcwd()

# Processa as imagens no diretório com os metadados fornecidos
process_images_in_directory(dir_path, description, subject, brands, latitude, longitude)

print("Script finalizado com sucesso!")
time.sleep(5)