import os
import struct
import threading
import hashlib
import hmac as hmac_mod
from datetime import datetime
from PIL import Image
import numpy as np

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

from kivy.utils import platform
if platform != "android":
    from kivy.core.window import Window
    Window.size = (420, 860)

def get_download_path():
    if platform == "android":
        return "/storage/emulated/0/Download"
    return os.getcwd()

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle

KV = """
<CyberButton@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: '16sp'
    bold: True
    size_hint_y: None
    height: '52dp'
    canvas.before:
        Color:
            rgba: (0.15, 0.0, 0.05, 1) if self.state == 'normal' else (0.55, 0.0, 0.12, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]
        Color:
            rgba: (0.7, 0.0, 0.18, 1) if self.state == 'normal' else (1.0, 0.2, 0.3, 1)
        Line:
            width: 1.2
            rounded_rectangle: (self.x, self.y, self.width, self.height, 12)

<GhostButton@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    color: 0.5, 0.5, 0.55, 1
    font_size: '14sp'
    size_hint_y: None
    height: '42dp'
    canvas.before:
        Color:
            rgba: (0.08, 0.08, 0.1, 1) if self.state == 'normal' else (0.15, 0.15, 0.18, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
        Color:
            rgba: (0.22, 0.22, 0.28, 1)
        Line:
            width: 1.0
            rounded_rectangle: (self.x, self.y, self.width, self.height, 10)

<SmallButton@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    color: 0.55, 0.55, 0.62, 1
    font_size: '13sp'
    size_hint_y: None
    height: '36dp'
    canvas.before:
        Color:
            rgba: (0.07, 0.07, 0.09, 1) if self.state == 'normal' else (0.14, 0.14, 0.18, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8,]
        Color:
            rgba: (0.18, 0.18, 0.24, 1)
        Line:
            width: 0.9
            rounded_rectangle: (self.x, self.y, self.width, self.height, 8)

<CardWidget@BoxLayout>:
    canvas.before:
        Color:
            rgba: 0.06, 0.03, 0.06, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [16,]
        Color:
            rgba: 0.2, 0.04, 0.09, 1
        Line:
            width: 1.0
            rounded_rectangle: (self.x, self.y, self.width, self.height, 16)

<WarnCard@BoxLayout>:
    canvas.before:
        Color:
            rgba: 0.09, 0.07, 0.01, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [14,]
        Color:
            rgba: 0.5, 0.38, 0.0, 1
        Line:
            width: 1.0
            rounded_rectangle: (self.x, self.y, self.width, self.height, 14)

<DividerLine@BoxLayout>:
    size_hint_y: None
    height: '1dp'
    canvas.before:
        Color:
            rgba: 0.22, 0.05, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size

<CyberProgress@ProgressBar>:
    max: 100
    canvas:
        Color:
            rgba: 0.1, 0.04, 0.1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [6,]
        Color:
            rgba: 0.85, 0.05, 0.2, 1
        RoundedRectangle:
            pos: self.pos
            size: (self.width * self.value_normalized, self.height)
            radius: [6,]

<BaseScreen>:
    canvas.before:
        Color:
            rgba: 0.04, 0.02, 0.04, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: 0.55, 0.0, 0.14, 0.06
        RoundedRectangle:
            pos: self.x - 60, self.y + self.height * 0.45
            size: self.width * 1.0, self.height * 0.65
            radius: [300,]

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [28, 44, 28, 28]
        spacing: 0
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: '158dp'
            spacing: 3
            BoxLayout:
                size_hint_y: None
                height: '78dp'
                Label:
                    text: 'SHADOW'
                    font_size: '46sp'
                    bold: True
                    color: 0.9, 0.05, 0.2, 1
                    halign: 'left'
                    valign: 'middle'
                    text_size: self.size
                SmallButton:
                    text: '?  Guide'
                    size_hint_x: None
                    width: '90dp'
                    on_release: root.manager.current = 'guide'
            Label:
                text: 'STEGANOGRAPHY  v3.0 PRO'
                font_size: '14sp'
                color: 0.4, 0.1, 0.2, 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                size_hint_y: None
                height: '24dp'
            Label:
                text: 'AES-256 encrypted  |  pixel shuffling'
                font_size: '11sp'
                color: 0.25, 0.25, 0.35, 1
                italic: True
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                size_hint_y: None
                height: '20dp'
        DividerLine
        Widget:
            size_hint_y: None
            height: '14dp'
        CardWidget:
            orientation: 'vertical'
            padding: [20, 14]
            spacing: 8
            size_hint_y: None
            height: '128dp'
            Label:
                text: 'Hide Secret'
                font_size: '15sp'
                bold: True
                color: 0.85, 0.85, 0.9, 1
                halign: 'left'
                text_size: self.size
                size_hint_y: None
                height: '22dp'
            Label:
                text: 'Encrypt and embed data inside an image'
                font_size: '11sp'
                color: 0.35, 0.35, 0.45, 1
                halign: 'left'
                text_size: self.size
            CyberButton:
                text: 'Hide Secret'
                on_release: root.go_hide()
        Widget:
            size_hint_y: None
            height: '8dp'
        CardWidget:
            orientation: 'vertical'
            padding: [20, 14]
            spacing: 8
            size_hint_y: None
            height: '128dp'
            Label:
                text: 'Extract Secret'
                font_size: '15sp'
                bold: True
                color: 0.85, 0.85, 0.9, 1
                halign: 'left'
                text_size: self.size
                size_hint_y: None
                height: '22dp'
            Label:
                text: 'Decrypt hidden data from an image'
                font_size: '11sp'
                color: 0.35, 0.35, 0.45, 1
                halign: 'left'
                text_size: self.size
            CyberButton:
                text: 'Extract Secret'
                on_release: root.go_extract()
        Widget:
            size_hint_y: None
            height: '10dp'
        WarnCard:
            orientation: 'vertical'
            padding: [14, 10]
            spacing: 3
            size_hint_y: None
            height: '66dp'
            Label:
                text: 'Telegram: Send as FILE not as Photo'
                font_size: '12sp'
                bold: True
                color: 1.0, 0.82, 0.1, 1
                halign: 'left'
                text_size: self.size
                size_hint_y: None
                height: '20dp'
            Label:
                text: 'Photo mode compresses and destroys the secret'
                font_size: '10sp'
                color: 0.62, 0.52, 0.18, 1
                halign: 'left'
                text_size: self.size
        Widget:
            size_hint_y: 1

<HideMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [28, 38, 28, 28]
        spacing: 12
        BoxLayout:
            size_hint_y: None
            height: '46dp'
            GhostButton:
                text: 'Back'
                size_hint_x: None
                width: '76dp'
                on_release: root.manager.current = 'main'
            Label:
                text: 'What to Hide?'
                font_size: '20sp'
                bold: True
                color: 0.85, 0.05, 0.2, 1
        CyberButton:
            text: 'Text Message'
            on_release: root.select_type('T')
        CyberButton:
            text: 'Audio File'
            on_release: root.select_type('A')
        CyberButton:
            text: 'Video Clip'
            on_release: root.select_type('V')
        CyberButton:
            text: 'Any File'
            on_release: root.select_type('F')
        Widget:
            size_hint_y: 1

<TextInputScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [28, 38, 28, 28]
        spacing: 14
        BoxLayout:
            size_hint_y: None
            height: '46dp'
            GhostButton:
                text: 'Back'
                size_hint_x: None
                width: '76dp'
                on_release: root.manager.current = 'hide_menu'
            Label:
                text: 'Secret Message'
                font_size: '20sp'
                bold: True
                color: 0.85, 0.05, 0.2, 1
        Label:
            text: 'Type your secret message:'
            font_size: '12sp'
            color: 0.35, 0.35, 0.45, 1
            size_hint_y: None
            height: '22dp'
        TextInput:
            id: txt_input
            background_color: 0.04, 0.02, 0.04, 1
            foreground_color: 0.9, 0.9, 0.95, 1
            cursor_color: 0.9, 0.05, 0.2, 1
            hint_text: 'Enter your secret here...'
            hint_text_color: 0.22, 0.1, 0.18, 1
            font_size: '15sp'
            padding: [14, 12]
            multiline: True
        CyberButton:
            text: 'Next: Set Password'
            on_release: root.process_text()

<PasswordScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [28, 38, 28, 28]
        spacing: 14
        BoxLayout:
            size_hint_y: None
            height: '46dp'
            GhostButton:
                text: 'Back'
                size_hint_x: None
                width: '76dp'
                on_release: root.go_back()
            Label:
                id: screen_title
                text: 'Set Password'
                font_size: '20sp'
                bold: True
                color: 0.85, 0.05, 0.2, 1
        Label:
            text: 'Choose a strong password to encrypt your secret'
            font_size: '12sp'
            color: 0.35, 0.35, 0.45, 1
            size_hint_y: None
            height: '22dp'
            halign: 'left'
            text_size: self.size
        CardWidget:
            orientation: 'vertical'
            padding: [18, 16]
            spacing: 12
            size_hint_y: None
            height: '168dp'
            Label:
                text: 'Password'
                font_size: '13sp'
                color: 0.5, 0.5, 0.6, 1
                halign: 'left'
                text_size: self.size
                size_hint_y: None
                height: '20dp'
            TextInput:
                id: pass_input
                background_color: 0.03, 0.01, 0.04, 1
                foreground_color: 0.9, 0.9, 0.95, 1
                cursor_color: 0.9, 0.05, 0.2, 1
                hint_text: 'Enter password...'
                hint_text_color: 0.22, 0.1, 0.18, 1
                font_size: '15sp'
                password: True
                multiline: False
                padding: [14, 12]
                size_hint_y: None
                height: '46dp'
            Label:
                text: 'Confirm Password'
                font_size: '13sp'
                color: 0.5, 0.5, 0.6, 1
                halign: 'left'
                text_size: self.size
                size_hint_y: None
                height: '20dp'
            TextInput:
                id: pass_confirm
                background_color: 0.03, 0.01, 0.04, 1
                foreground_color: 0.9, 0.9, 0.95, 1
                cursor_color: 0.9, 0.05, 0.2, 1
                hint_text: 'Confirm password...'
                hint_text_color: 0.22, 0.1, 0.18, 1
                font_size: '15sp'
                password: True
                multiline: False
                padding: [14, 12]
                size_hint_y: None
                height: '46dp'
        Label:
            id: strength_label
            text: ''
            font_size: '12sp'
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: '20dp'
            halign: 'left'
            text_size: self.size
        CyberButton:
            text: 'Next: Pick Carrier Image'
            on_release: root.confirm_password()
        Widget:
            size_hint_y: 1

<ExtractPasswordScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [28, 38, 28, 28]
        spacing: 14
        BoxLayout:
            size_hint_y: None
            height: '46dp'
            GhostButton:
                text: 'Back'
                size_hint_x: None
                width: '76dp'
                on_release: root.manager.current = 'main'
            Label:
                text: 'Enter Password'
                font_size: '20sp'
                bold: True
                color: 0.85, 0.05, 0.2, 1
        Label:
            text: 'Enter the password used when hiding the secret'
            font_size: '12sp'
            color: 0.35, 0.35, 0.45, 1
            size_hint_y: None
            height: '22dp'
            halign: 'left'
            text_size: self.size
        CardWidget:
            orientation: 'vertical'
            padding: [18, 16]
            spacing: 10
            size_hint_y: None
            height: '96dp'
            Label:
                text: 'Password'
                font_size: '13sp'
                color: 0.5, 0.5, 0.6, 1
                halign: 'left'
                text_size: self.size
                size_hint_y: None
                height: '20dp'
            TextInput:
                id: pass_input
                background_color: 0.03, 0.01, 0.04, 1
                foreground_color: 0.9, 0.9, 0.95, 1
                cursor_color: 0.9, 0.05, 0.2, 1
                hint_text: 'Enter password...'
                hint_text_color: 0.22, 0.1, 0.18, 1
                font_size: '15sp'
                password: True
                multiline: False
                padding: [14, 12]
                size_hint_y: None
                height: '46dp'
        CyberButton:
            text: 'Next: Pick Image'
            on_release: root.confirm_password()
        Widget:
            size_hint_y: 1

<FilePickerScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [14, 28, 14, 14]
        spacing: 10
        BoxLayout:
            size_hint_y: None
            height: '46dp'
            spacing: 8
            GhostButton:
                text: 'Back'
                size_hint_x: None
                width: '76dp'
                on_release: root.go_back()
            Label:
                id: screen_title
                text: 'Select File'
                font_size: '18sp'
                bold: True
                color: 0.85, 0.05, 0.2, 1
        Label:
            id: hint_label
            text: ''
            font_size: '11sp'
            color: 0.35, 0.35, 0.45, 1
            size_hint_y: None
            height: '18dp'
        FileChooserListView:
            id: file_chooser
            path: "/storage/emulated/0" if app.is_android else "."
            color: 0.85, 0.85, 0.9, 1
        CyberButton:
            text: 'Confirm'
            on_release: root.file_selected(file_chooser.selection)

<LoadingScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [40, 80]
        spacing: 18
        Label:
            id: loading_icon
            text: 'O'
            font_size: '58sp'
            bold: True
            color: 0.9, 0.05, 0.2, 1
            size_hint_y: None
            height: '80dp'
        Label:
            id: loading_title
            text: 'Processing...'
            font_size: '20sp'
            bold: True
            color: 0.85, 0.85, 0.9, 1
            size_hint_y: None
            height: '34dp'
        Label:
            id: loading_sub
            text: 'Please wait...'
            font_size: '13sp'
            color: 0.4, 0.4, 0.5, 1
            size_hint_y: None
            height: '24dp'
        Widget:
            size_hint_y: None
            height: '16dp'
        CyberProgress:
            id: progress_bar
            value: 0
            size_hint_y: None
            height: '14dp'
        Label:
            id: progress_label
            text: '0%'
            font_size: '12sp'
            color: 0.5, 0.5, 0.6, 1
            size_hint_y: None
            height: '22dp'
        Widget:
            size_hint_y: 1

<ExtractResultScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [28, 38, 28, 28]
        spacing: 12
        BoxLayout:
            size_hint_y: None
            height: '46dp'
            GhostButton:
                text: 'Home'
                size_hint_x: None
                width: '76dp'
                on_release: root.manager.current = 'main'
            Label:
                text: 'Extracted Secret'
                font_size: '20sp'
                bold: True
                color: 0.85, 0.05, 0.2, 1
        Label:
            id: status_badge
            text: 'Decrypted and extracted successfully'
            font_size: '12sp'
            color: 0.2, 0.88, 0.4, 1
            size_hint_y: None
            height: '24dp'
        TextInput:
            id: result_view
            background_color: 0.03, 0.01, 0.04, 1
            foreground_color: 0.85, 0.9, 0.95, 1
            hint_text: 'Extracted text appears here...'
            font_size: '14sp'
            readonly: True
            padding: [14, 12]
        Label:
            id: file_saved_label
            text: ''
            font_size: '11sp'
            color: 0.4, 0.6, 0.9, 1
            size_hint_y: None
            height: '20dp'
        GhostButton:
            text: 'New Operation'
            on_release: root.manager.current = 'main'

<GuideScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [28, 38, 28, 28]
        spacing: 12
        BoxLayout:
            size_hint_y: None
            height: '46dp'
            GhostButton:
                text: 'Back'
                size_hint_x: None
                width: '76dp'
                on_release: root.manager.current = 'main'
            Label:
                text: 'Guide'
                font_size: '20sp'
                bold: True
                color: 0.85, 0.05, 0.2, 1
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                orientation: 'vertical'
                padding: [18, 16]
                spacing: 14
                size_hint_y: None
                height: self.minimum_height
                canvas.before:
                    Color:
                        rgba: 0.06, 0.03, 0.06, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [16,]
                    Color:
                        rgba: 0.2, 0.04, 0.09, 1
                    Line:
                        width: 1.0
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 16)
                Label:
                    id: guide_content
                    text: app.guide_text
                    font_size: '13sp'
                    color: 0.72, 0.72, 0.78, 1
                    halign: 'right'
                    valign: 'top'
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1]
"""


# ─── CRYPTO ENGINE ───────────────────────────────────────────────
class CryptoEngine:
    SALT_SIZE  = 16
    NONCE_SIZE = 12
    KEY_SIZE   = 32

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        if HAS_CRYPTO:
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                             length=CryptoEngine.KEY_SIZE,
                             salt=salt, iterations=200_000)
            return kdf.derive(password.encode('utf-8'))
        raw = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200_000,
                                  dklen=CryptoEngine.KEY_SIZE)
        return raw

    @staticmethod
    def encrypt(password: str, plaintext: bytes) -> bytes:
        salt  = os.urandom(CryptoEngine.SALT_SIZE)
        nonce = os.urandom(CryptoEngine.NONCE_SIZE)
        key   = CryptoEngine.derive_key(password, salt)
        if HAS_CRYPTO:
            ct = AESGCM(key).encrypt(nonce, plaintext, None)
        else:
            ct = CryptoEngine._xor_stream(key, nonce, plaintext)
            ct += hmac_mod.new(key, ct, hashlib.sha256).digest()
        return salt + nonce + ct

    @staticmethod
    def decrypt(password: str, blob: bytes) -> bytes:
        s  = CryptoEngine.SALT_SIZE
        n  = CryptoEngine.NONCE_SIZE
        salt, nonce, ct = blob[:s], blob[s:s+n], blob[s+n:]
        key = CryptoEngine.derive_key(password, salt)
        if HAS_CRYPTO:
            try:
                return AESGCM(key).decrypt(nonce, ct, None)
            except Exception:
                raise ValueError("Wrong password or corrupted data")
        else:
            mac, ct2 = ct[-32:], ct[:-32]
            expected = hmac_mod.new(key, ct2, hashlib.sha256).digest()
            if not hmac_mod.compare_digest(mac, expected):
                raise ValueError("Wrong password or corrupted data")
            return CryptoEngine._xor_stream(key, nonce, ct2)

    @staticmethod
    def _xor_stream(key, nonce, data):
        ks = b''
        for i in range((len(data) // 32) + 2):
            ks += hashlib.sha256(key + nonce + i.to_bytes(4, 'little')).digest()
        return bytes(a ^ b for a, b in zip(data, ks))


# ─── STEGO ENGINE ────────────────────────────────────────────────
class StegoEngine:
    MAGIC   = b'SHDW'
    VERSION = b'\x03'

    @staticmethod
    def _indices(password: str, total: int, count: int) -> np.ndarray:
        seed = int.from_bytes(
            hashlib.sha256(password.encode('utf-8')).digest()[:8], 'little'
        )
        return np.random.default_rng(seed).choice(total, size=count, replace=False)

    @staticmethod
    def embed(carrier, payload, p_type, password, out, progress_cb=None):
        def prog(v, msg):
            if progress_cb:
                Clock.schedule_once(lambda dt: progress_cb(v, msg))

        img = Image.open(carrier)
        rgba = (img.mode == 'RGBA')
        img  = img.convert('RGBA' if rgba else 'RGB')
        arr  = np.array(img, dtype=np.uint8)
        ch   = 4 if rgba else 3

        prog(5, 'Encrypting...')
        encrypted = CryptoEngine.encrypt(password, payload)

        header     = StegoEngine.MAGIC + StegoEngine.VERSION + p_type.encode() + struct.pack('<Q', len(encrypted))
        data       = header + encrypted
        total_bits = len(data) * 8

        flat = arr[:, :, :ch].flatten().copy()
        if total_bits > len(flat):
            raise ValueError(
                f"Image too small.\n"
                f"Need {len(data):,} bytes capacity.\n"
                f"Image holds {len(flat)//8:,} bytes.\n"
                f"Use a larger image."
            )

        prog(20, 'Shuffling positions...')
        idx  = StegoEngine._indices(password, len(flat), total_bits)
        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))

        prog(40, 'Embedding...')
        flat[idx] = (flat[idx] & 0xFE) | bits

        prog(85, 'Saving image...')
        result = flat.reshape(arr[:, :, :ch].shape).astype(np.uint8)
        arr[:, :, :ch] = result
        Image.fromarray(arr[:, :, :ch], 'RGBA' if rgba else 'RGB').save(out, 'PNG', optimize=False)
        prog(100, 'Done!')

    @staticmethod
    def extract(path, password, progress_cb=None):
        def prog(v, msg):
            if progress_cb:
                Clock.schedule_once(lambda dt: progress_cb(v, msg))

        img  = Image.open(path)
        rgba = (img.mode == 'RGBA')
        img  = img.convert('RGBA' if rgba else 'RGB')
        arr  = np.array(img, dtype=np.uint8)
        ch   = 4 if rgba else 3
        flat = arr[:, :, :ch].flatten()

        # Header = MAGIC(4) + VER(1) + TYPE(1) + SIZE(8) = 14 bytes = 112 bits
        HDR = 14 * 8
        prog(10, 'Reading header...')
        idx_hdr  = StegoEngine._indices(password, len(flat), HDR)
        hdr_bits = flat[idx_hdr] & 1
        hdr      = bytes(np.packbits(hdr_bits.reshape(14, 8)))

        if hdr[:4] != StegoEngine.MAGIC:
            return None, None

        p_type = chr(hdr[5])
        size   = struct.unpack('<Q', hdr[6:14])[0]
        if size == 0 or size > 100_000_000 or HDR + size*8 > len(flat):
            return None, None

        prog(30, 'Extracting data...')
        idx_all  = StegoEngine._indices(password, len(flat), HDR + size*8)
        all_bits = flat[idx_all] & 1
        enc      = bytes(np.packbits(all_bits[HDR:].reshape(-1, 8)))

        prog(70, 'Decrypting...')
        payload = CryptoEngine.decrypt(password, enc)
        prog(100, 'Done!')
        return p_type, payload


# ─── SCREENS ────────────────────────────────────────────────────
class BaseScreen(Screen):
    pass

class MainScreen(BaseScreen):
    def go_hide(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'hide_menu'
    def go_extract(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'extract_password'

class HideMenuScreen(BaseScreen):
    def select_type(self, t):
        App.get_running_app().current_payload_type = t
        self.manager.transition = SlideTransition(direction='left')
        if t == 'T':
            self.manager.current = 'text_input'
        else:
            fp = self.manager.get_screen('file_picker')
            fp.mode = 'payload'
            fp.ids.screen_title.text = 'Select File to Hide'
            fp.ids.hint_label.text = 'Choose the file you want to embed'
            self.manager.current = 'file_picker'

class TextInputScreen(BaseScreen):
    def process_text(self):
        msg = self.ids.txt_input.text.strip()
        if not msg:
            _popup('Error', 'Please enter a message first.', error=True)
            return
        App.get_running_app().payload_bytes = msg.encode('utf-8')
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'password'

class PasswordScreen(BaseScreen):
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        t = App.get_running_app().current_payload_type
        self.manager.current = 'text_input' if t == 'T' else 'hide_menu'

    def on_enter(self):
        self.ids.pass_input.text = ''
        self.ids.pass_confirm.text = ''
        self.ids.strength_label.text = ''
        self.ids.pass_input.bind(text=self._strength)

    def _strength(self, inst, val):
        if not val:
            self.ids.strength_label.text = ''
            return
        s = sum([len(val)>=8, len(val)>=12,
                 any(c.isdigit() for c in val),
                 any(c.isupper() for c in val),
                 any(c in '!@#$%^&*' for c in val)])
        labels = ['Weak','Fair','Good','Strong','Very Strong']
        self.ids.strength_label.text = f"Strength: {labels[min(s,4)]}"

    def confirm_password(self):
        p1, p2 = self.ids.pass_input.text, self.ids.pass_confirm.text
        if not p1:
            _popup('Error', 'Please enter a password.', error=True); return
        if p1 != p2:
            _popup('Error', 'Passwords do not match.', error=True); return
        if len(p1) < 6:
            _popup('Error', 'Password must be at least 6 characters.', error=True); return
        App.get_running_app().current_password = p1
        fp = self.manager.get_screen('file_picker')
        fp.mode = 'carrier'
        fp.ids.screen_title.text = 'Select Carrier Image'
        fp.ids.hint_label.text = 'Pick the image that will carry the secret'
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'file_picker'

class ExtractPasswordScreen(BaseScreen):
    def on_enter(self):
        self.ids.pass_input.text = ''
    def confirm_password(self):
        pwd = self.ids.pass_input.text
        if not pwd:
            _popup('Error', 'Please enter the password.', error=True); return
        App.get_running_app().current_password = pwd
        fp = self.manager.get_screen('file_picker')
        fp.mode = 'extract'
        fp.ids.screen_title.text = 'Select Stego Image'
        fp.ids.hint_label.text = 'Pick the image with the hidden data'
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'file_picker'

class FilePickerScreen(BaseScreen):
    mode = StringProperty('payload')

    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = {
            'payload': 'hide_menu',
            'carrier': 'password',
            'extract': 'extract_password'
        }.get(self.mode, 'main')

    def file_selected(self, selection):
        if not selection:
            _popup('Error', 'Please select a file first.', error=True); return
        path = selection[0]
        app  = App.get_running_app()
        if self.mode == 'payload':
            with open(path, 'rb') as f:
                app.payload_bytes = f.read()
            self.mode = 'carrier'
            self.ids.screen_title.text = 'Select Carrier Image'
            self.ids.hint_label.text   = 'Now pick the image that will hide it'
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'password'
        elif self.mode == 'carrier':
            self._run_embed(path)
        elif self.mode == 'extract':
            self._run_extract(path)

    def _prog(self, v, lbl=''):
        ls = self.manager.get_screen('loading')
        ls.ids.progress_bar.value   = v
        ls.ids.progress_label.text  = f"{int(v)}%  {lbl}"

    def _loading(self, title, sub):
        ls = self.manager.get_screen('loading')
        ls.ids.loading_title.text  = title
        ls.ids.loading_sub.text    = sub
        ls.ids.progress_bar.value  = 0
        ls.ids.progress_label.text = '0%'
        self.manager.transition = FadeTransition(duration=0.18)
        self.manager.current = 'loading'

    def _run_embed(self, carrier):
        app = App.get_running_app()
        out = os.path.join(get_download_path(), f"SHADOW_{datetime.now().strftime('%H%M%S')}.png")
        self._loading('Hiding Secret...', 'Encrypting and embedding...')
        def task():
            try:
                StegoEngine.embed(carrier, app.payload_bytes, app.current_payload_type,
                                  app.current_password, out, progress_cb=self._prog)
                Clock.schedule_once(lambda dt: self._done_embed(out))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._err(str(e)))
        threading.Thread(target=task, daemon=True).start()

    def _done_embed(self, out):
        self.manager.transition = FadeTransition(duration=0.25)
        self.manager.current = 'main'
        _popup('Mission Complete',
               f"Saved: {os.path.basename(out)}\n\n"
               f"Encrypted with AES-256.\n"
               f"Telegram: send as FILE not as Photo!")

    def _run_extract(self, path):
        app = App.get_running_app()
        self._loading('Extracting...', 'Decrypting hidden data...')
        def task():
            try:
                t, p = StegoEngine.extract(path, app.current_password, progress_cb=self._prog)
                Clock.schedule_once(lambda dt: self._done_extract(t, p))
            except ValueError as e:
                Clock.schedule_once(lambda dt: self._err(str(e)))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._err(str(e)))
        threading.Thread(target=task, daemon=True).start()

    def _done_extract(self, p_type, payload):
        if p_type is None:
            self._err("No hidden data found.\n\nCheck:\n- Correct password?\n- Image sent as FILE?\n- Created with this app?")
            return
        scr = self.manager.get_screen('extract_result')
        if p_type == 'T':
            scr.ids.result_view.text    = payload.decode('utf-8', errors='ignore')
            scr.ids.file_saved_label.text = ''
        else:
            ext  = {'A':'mp3','V':'mp4'}.get(p_type,'bin')
            path = os.path.join(get_download_path(), f"EXTRACTED_{datetime.now().strftime('%H%M%S')}.{ext}")
            open(path,'wb').write(payload)
            scr.ids.result_view.text    = f"File extracted\nSize: {len(payload):,} bytes"
            scr.ids.file_saved_label.text = f"Saved: {os.path.basename(path)}"
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'extract_result'

    def _err(self, msg):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'
        _popup('Failed', msg, error=True)

class LoadingScreen(BaseScreen):
    def on_enter(self):
        self._ev = Clock.schedule_interval(self._pulse, 1.0)
    def on_leave(self):
        if hasattr(self, '_ev'): self._ev.cancel()
    def _pulse(self, dt):
        a = Animation(opacity=0.15, duration=0.5) + Animation(opacity=1.0, duration=0.5)
        a.start(self.ids.loading_icon)

class ExtractResultScreen(BaseScreen):
    pass

class GuideScreen(BaseScreen):
    pass


# ─── POPUP ──────────────────────────────────────────────────────
def _popup(title, msg, error=False):
    p = Popup(title=title, size_hint=(0.88, 0.48),
              background_color=(0.06, 0.03, 0.06, 1),
              title_color=(0.9,0.05,0.2,1) if not error else (1.0,0.28,0.08,1))
    box = BoxLayout(orientation='vertical', padding=14, spacing=10)
    lbl = Label(text=msg, color=(0.85,0.85,0.9,1), font_size='13sp',
                halign='center', valign='top')
    lbl.bind(size=lambda *a: setattr(lbl,'text_size',lbl.size))
    box.add_widget(lbl)
    btn = Button(text='OK', size_hint_y=None, height='44dp',
                 background_color=(0.18,0.0,0.06,1), color=(1,1,1,1))
    btn.bind(on_release=p.dismiss)
    box.add_widget(btn)
    p.content = box
    p.open()


# ─── APP ────────────────────────────────────────────────────────
GUIDE_TEXT = (
    "Shadow Steganography v3.0 PRO\n"
    "تشفير AES-256 مع توزيع عشوائي للبيانات\n\n"
    "─────────────────────────────\n"
    "كيفية اخفاء سر\n"
    "─────────────────────────────\n\n"
    "1  اضغط Hide Secret من الشاشة الرئيسية\n\n"
    "2  اختر نوع ما تريد اخفاءه\n"
    "   نص - ملف صوتي - فيديو - اي ملف\n\n"
    "3  اكتب رسالتك اذا اخترت النص\n\n"
    "4  اختر كلمة مرور قوية ولا تنساها\n"
    "   بدونها لن تستطيع استخراج السر ابدا\n\n"
    "5  اختر صورة حاملة من جهازك\n"
    "   كلما كانت الصورة اكبر كانت السعة اعلى\n\n"
    "6  انتظر المعالجة\n"
    "   الصورة تُحفظ تلقائيا في مجلد التنزيلات\n\n"
    "─────────────────────────────\n"
    "كيفية استخراج السر\n"
    "─────────────────────────────\n\n"
    "1  اضغط Extract Secret\n\n"
    "2  ادخل كلمة المرور التي استخدمتها\n\n"
    "3  اختر الصورة التي تحتوي على السر\n\n"
    "4  النص يظهر مباشرة\n"
    "   الملفات تُحفظ في التنزيلات\n\n"
    "─────────────────────────────\n"
    "مهم جدا - الارسال الآمن\n"
    "─────────────────────────────\n\n"
    "تيليكرام وواتساب يضغطان الصور\n"
    "وهذا يدمر السر المخفي تماما\n\n"
    "الحل الصحيح:\n"
    "ضع الصورة داخل ملف مضغوط ZIP\n"
    "او داخل ملف Word ثم ارسل الملف\n\n"
    "في تيليكرام:\n"
    "اضغط مشبك الورق ثم اختر File\n"
    "وليس Photo or Video\n\n"
    "في واتساب:\n"
    "اضغط مشبك الورق ثم اختر Document\n\n"
    "المستلم يحفظ الملف ويفتح الصورة\n"
    "بهذا التطبيق لاستخراج السر\n\n"
    "─────────────────────────────\n"
    "نصائح مهمة\n"
    "─────────────────────────────\n\n"
    "استخدم صورا PNG وليس JPEG\n\n"
    "لا تضغط الصورة الناتجة ابدا\n\n"
    "احتفظ بكلمة المرور في مكان آمن\n\n"
    "يمكن تبادل رسائل متعددة بنفس\n"
    "كلمة المرور مع نفس الشخص\n\n"
    "المنصات الآمنة للمشاركة:\n"
    "تيليكرام File - واتساب Document\n"
    "ديسكورد - البريد الالكتروني\n"
    "USB - AirDrop\n\n"
    "المنصات الخطرة التي تدمر السر:\n"
    "تيليكرام Photo - انستغرام\n"
    "تويتر - فيسبوك - سناب شات"
)


class ShadowStegoApp(App):
    guide_text = GUIDE_TEXT

    def build(self):
        self.is_android          = (platform == "android")
        self.current_payload_type = 'T'
        self.payload_bytes        = b''
        self.current_password     = ''
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(HideMenuScreen(name='hide_menu'))
        sm.add_widget(TextInputScreen(name='text_input'))
        sm.add_widget(PasswordScreen(name='password'))
        sm.add_widget(ExtractPasswordScreen(name='extract_password'))
        sm.add_widget(FilePickerScreen(name='file_picker'))
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(ExtractResultScreen(name='extract_result'))
        sm.add_widget(GuideScreen(name='guide'))
        return sm


if __name__ == "__main__":
    ShadowStegoApp().run()