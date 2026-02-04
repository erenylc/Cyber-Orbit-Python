## Kaçış Oyunu (Python + Pygame)

Basit bir 2D kaçış oyunu. Oyuncu kareyi klavyeyle hareket ettirerek yukarıdan düşen kırmızı bloklardan kaçmaya çalışır.

### Kurulum

1. Python kurulu olduğundan emin olun.
2. Bu klasörde bir terminal / PowerShell açın.
3. Gerekli kütüphaneyi yükleyin:

```bash
pip install -r requirements.txt
```

Eğer `pip` komutu çalışmazsa:

```bash
py -m pip install -r requirements.txt
```

### Çalıştırma

Bu klasörde:

```bash
python main.py
```

veya:

```bash
py main.py
```

### Kontroller

- Yön tuşları veya **W / A / S / D** ile hareket.
- Çarpışırsan **OYUN BİTTİ** ekranı gelir.
- **R**: Yeniden başlat.
- **ESC**: Çıkış.
