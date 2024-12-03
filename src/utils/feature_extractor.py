import os
import struct
import math
from collections import OrderedDict

class FeatureExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.features = OrderedDict()
        self.calculate_features()

    def calculate_features(self):
        self.features['is_mp3'] = self.check_mp3()
        self.features['is_mp4'] = self.check_mp4()
        self.features['is_jpg'] = self.check_jpg()
        self.features['is_png'] = self.check_png()
        self.features['is_wav'] = self.check_wav()
        self.features['has_spaces_or_newlines'] = self.check_spaces_or_newlines()
        self.features['entropy'] = self.calculate_entropy()
        self.features['is_even_weight'] = self.check_even_weight()

    def check_mp3(self):
        with open(self.file_path, 'rb') as f:
            header = f.read(3)
            return header == b'ID3'

    def check_mp4(self):
        with open(self.file_path, 'rb') as f:
            header = f.read(8)
            return header[:4] == b'ftyp'

    def check_jpg(self):
        with open(self.file_path, 'rb') as f:
            header = f.read(2)
            return header == b'\xff\xd8'

    def check_png(self):
        with open(self.file_path, 'rb') as f:
            header = f.read(8)
            return header == b'\x89PNG\r\n\x1a\n'

    def check_wav(self):
        with open(self.file_path, 'rb') as f:
            header = f.read(4)
            return header == b'RIFF'

    def check_spaces_or_newlines(self):
        with open(self.file_path, 'rb') as f:
            content = f.read()
            return b'\x0D' in content or b'\x0A' in content

    def calculate_entropy(self):
        with open(self.file_path, 'rb') as f:
            content = f.read()
            byte_counts = [0] * 256
            for byte in content:
                byte_counts[byte] += 1
            entropy = 0.0
            file_size = len(content)
            for count in byte_counts:
                if count > 0:
                    probability = count / file_size
                    entropy -= probability * math.log2(probability)
            return entropy

    def check_even_weight(self):
        file_size = os.path.getsize(self.file_path)
        return file_size % 2 == 0

    def get_features(self):
        return self.features

#дальше мои примеры какие-то, но в целом работает
file_path = '/Users/force/test_out/rep.md.Blowfish.enc'
extractor = FeatureExtractor(file_path)
features = extractor.get_features()
print(features)