import os
import zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Функция для генерации ключа и IV (вектора инициализации)
def generate_key_and_iv(algorithm):
    if algorithm == 'AES':
        key = os.urandom(32)  # 256-битный ключ для AES-256
        iv = os.urandom(16)   # 128-битный IV для AES
    elif algorithm == 'Blowfish':
        key = os.urandom(16)  # 128-битный ключ для Blowfish
        iv = os.urandom(8)    # 64-битный IV для Blowfish
    else:
        raise ValueError("Неподдерживаемый алгоритм шифрования")
    return key, iv

# Функция для сохранения ключа и IV в файл
def save_key_and_iv(key, iv, filename):
    with open(filename, 'wb') as f:
        f.write(key)
        f.write(iv)

# Функция для загрузки ключа и IV из файла
def load_key_and_iv(filename, algorithm):
    with open(filename, 'rb') as f:
        if algorithm == 'AES':
            key = f.read(32)
            iv = f.read(16)
        elif algorithm == 'Blowfish':
            key = f.read(16)
            iv = f.read(8)
        else:
            raise ValueError("Неподдерживаемый алгоритм шифрования")
    return key, iv

# Функция для шифрования данных
def encrypt_file(input_file, output_file, key, iv, algorithm):
    if algorithm == 'AES':
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    elif algorithm == 'Blowfish':
        from cryptography.hazmat.primitives.ciphers.algorithms import Blowfish
        cipher = Cipher(Blowfish(key), modes.CFB(iv), backend=default_backend())
    else:
        raise ValueError("Неподдерживаемый алгоритм шифрования")

    encryptor = cipher.encryptor()

    with open(input_file, 'rb') as f:
        plaintext = f.read()

    # Добавляем паддинг, если необходимо
    padder = padding.PKCS7(cipher.algorithm.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    # Шифруем данные
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    with open(output_file, 'wb') as f:
        f.write(ciphertext)

# Функция для сжатия данных
def compress_file(input_file, output_file):
    with open(input_file, 'rb') as f:
        plaintext = f.read()

    # Сжимаем данные с использованием DEFLATE
    compressed_data = zlib.compress(plaintext)

    with open(output_file, 'wb') as f:
        f.write(compressed_data)

# Функция для обработки всех файлов в папке
def process_folder(input_folder, output_folder, key, iv, algorithm, compress=False):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        input_file = os.path.join(input_folder, filename)
        if compress:
            output_file = os.path.join(output_folder, filename + '.compressed')
            compress_file(input_file, output_file)
            print(f"Сжат файл: {input_file} -> {output_file}")
        else:
            output_file = os.path.join(output_folder, filename + f'.{algorithm}.enc')
            encrypt_file(input_file, output_file, key, iv, algorithm)
            print(f"Зашифрован файл: {input_file} -> {output_file} с использованием {algorithm}")

if __name__ == "__main__":
    input_folder = "/Users/force/test_in"
    output_folder = "/Users/force/test_out"
    key_file_aes = "key_iv_aes.bin"
    key_file_blowfish = "key_iv_blowfish.bin"

    # Генерируем и сохраняем ключи и IV для AES
    key_aes, iv_aes = generate_key_and_iv('AES')
    save_key_and_iv(key_aes, iv_aes, key_file_aes)

    # Генерируем и сохраняем ключи и IV для Blowfish
    key_blowfish, iv_blowfish = generate_key_and_iv('Blowfish')
    save_key_and_iv(key_blowfish, iv_blowfish, key_file_blowfish)

    # Загружаем ключи и IV для AES
    key_aes, iv_aes = load_key_and_iv(key_file_aes, 'AES')

    # Загружаем ключи и IV для Blowfish
    key_blowfish, iv_blowfish = load_key_and_iv(key_file_blowfish, 'Blowfish')

    # Шифруем все файлы в папке с использованием AES
    process_folder(input_folder, output_folder, key_aes, iv_aes, 'AES')

    # Шифруем все файлы в папке с использованием Blowfish
    process_folder(input_folder, output_folder, key_blowfish, iv_blowfish, 'Blowfish')

    # Сжимаем все исходные файлы
    process_folder(input_folder, output_folder, None, None, None, compress=True)

    print("Шифрование и сжатие завершено.")