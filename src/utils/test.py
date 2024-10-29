import os
import zlib
import lzma
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

# Функция для генерации ключа и IV (вектора инициализации)
def generate_key_and_iv(algorithm):
    if algorithm == 'AES':
        key = os.urandom(32)  # 256-битный ключ для AES-256
        iv = os.urandom(16)   # 128-битный IV для AES
    elif algorithm == 'Blowfish':
        key = os.urandom(16)  # 128-битный ключ для Blowfish
        iv = os.urandom(8)    # 64-битный IV для Blowfish
    elif algorithm == 'ChaCha20':
        key = os.urandom(32)  # 256-битный ключ для ChaCha20
        iv = os.urandom(12)   # 96-битный nonce для ChaCha20
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
        elif algorithm == 'ChaCha20':
            key = f.read(32)
            iv = f.read(12)
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
    elif algorithm == 'ChaCha20':
        cipher = ChaCha20Poly1305(key)
    else:
        raise ValueError("Неподдерживаемый алгоритм шифрования")

    with open(input_file, 'rb') as f:
        plaintext = f.read()

    if algorithm == 'ChaCha20':
        # Шифруем данные с использованием ChaCha20Poly1305
        ciphertext = cipher.encrypt(iv, plaintext, None)
    else:
        # Добавляем паддинг, если необходимо
        padder = padding.PKCS7(cipher.algorithm.block_size).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        # Шифруем данные
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    with open(output_file, 'wb') as f:
        f.write(ciphertext)

# Функция для сжатия данных
def compress_file(input_file, output_file, compression_algorithm):
    with open(input_file, 'rb') as f:
        plaintext = f.read()

    if compression_algorithm == 'zlib':
        # Сжимаем данные с использованием DEFLATE
        compressed_data = zlib.compress(plaintext)
    elif compression_algorithm == 'lzma':
        # Сжимаем данные с использованием LZMA
        compressed_data = lzma.compress(plaintext)
    else:
        raise ValueError("Неподдерживаемый алгоритм сжатия")

    with open(output_file, 'wb') as f:
        f.write(compressed_data)

# Функция для обработки всех файлов в папке
def process_folder(input_folder, output_folder, key, iv, algorithm, compression_algorithm=None):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        input_file = os.path.join(input_folder, filename)
        if compression_algorithm:
            output_file = os.path.join(output_folder, filename + f'.{compression_algorithm}.compressed')
            compress_file(input_file, output_file, compression_algorithm)
            print(f"Сжат файл: {input_file} -> {output_file} с использованием {compression_algorithm}")
        else:
            output_file = os.path.join(output_folder, filename + f'.{algorithm}.enc')
            encrypt_file(input_file, output_file, key, iv, algorithm)
            print(f"Зашифрован файл: {input_file} -> {output_file} с использованием {algorithm}")

if __name__ == "__main__":
    input_folder = "/Users/force/test_in"
    output_folder = "/Users/force/test_out"
    key_file_aes = "key_iv_aes.bin"
    key_file_blowfish = "key_iv_blowfish.bin"
    key_file_chacha20 = "key_iv_chacha20.bin"

    # Генерируем и сохраняем ключи и IV для AES
    key_aes, iv_aes = generate_key_and_iv('AES')
    save_key_and_iv(key_aes, iv_aes, key_file_aes)

    # Генерируем и сохраняем ключи и IV для Blowfish
    key_blowfish, iv_blowfish = generate_key_and_iv('Blowfish')
    save_key_and_iv(key_blowfish, iv_blowfish, key_file_blowfish)

    # Генерируем и сохраняем ключи и IV для ChaCha20
    key_chacha20, iv_chacha20 = generate_key_and_iv('ChaCha20')
    save_key_and_iv(key_chacha20, iv_chacha20, key_file_chacha20)

    # Загружаем ключи и IV для AES
    key_aes, iv_aes = load_key_and_iv(key_file_aes, 'AES')

    # Загружаем ключи и IV для Blowfish
    key_blowfish, iv_blowfish = load_key_and_iv(key_file_blowfish, 'Blowfish')

    # Загружаем ключи и IV для ChaCha20
    key_chacha20, iv_chacha20 = load_key_and_iv(key_file_chacha20, 'ChaCha20')

    # Шифруем все файлы в папке с использованием AES
    process_folder(input_folder, output_folder, key_aes, iv_aes, 'AES')

    # Шифруем все файлы в папке с использованием Blowfish
    process_folder(input_folder, output_folder, key_blowfish, iv_blowfish, 'Blowfish')

    # Шифруем все файлы в папке с использованием ChaCha20
    process_folder(input_folder, output_folder, key_chacha20, iv_chacha20, 'ChaCha20')

    # Сжимаем все исходные файлы с использованием zlib
    process_folder(input_folder, output_folder, None, None, None, compression_algorithm='zlib')

    # Сжимаем все исходные файлы с использованием lzma
    process_folder(input_folder, output_folder, None, None, None, compression_algorithm='lzma')

    print("Шифрование и сжатие завершено.")
    