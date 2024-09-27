from setuptools import setup, find_packages

setup(
    name="wp_message",  # Kütüphanenin adı
    version="0.1.0",  # Sürüm numarası
    packages=find_packages(),  # Otomatik olarak tüm paketleri bul
    install_requires=[],  # Gereken bağımlılıklar
    description="Send WhatsApp message via chromium",
    author="kemkum",
    author_email="kondakci.k@gmail.com",
    url="https://github.com/seninusername/wp_message",  # GitHub linki
)