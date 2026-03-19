from __future__ import annotations

import base64
import io
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"

HOME_ICON = ":material/home:"
SIMULADOR_ICON = ":material/calculate:"
COMO_FUNCIONA_ICON = ":material/menu_book:"
GLOSSARIO_ICON = ":material/book:"
PLANOS_ICON = ":material/list_alt:"
CONTATO_ICON = ":material/mail:"


def asset_path(filename: str) -> Path:
    return ASSETS_DIR / filename


def _crop_uniform_border(img: Image.Image, tol: int = 24, pad: int = 2) -> Image.Image:
    """
    Corta bordas uniformes (claras, escuras ou neutras) ao redor da imagem.
    """
    if "A" in img.getbands():
        alpha = img.getchannel("A")
        bbox = alpha.getbbox()
        if bbox and bbox != (0, 0, *img.size):
            left, top, right, bottom = bbox
            left = max(0, left - pad)
            top = max(0, top - pad)
            right = min(img.size[0], right + pad)
            bottom = min(img.size[1], bottom + pad)
            img = img.crop((left, top, right, bottom))

    rgb = img.convert("RGB")
    arr = np.asarray(rgb).astype(np.int16)

    border = np.concatenate(
        [
            arr[0, :, :],
            arr[-1, :, :],
            arr[:, 0, :],
            arr[:, -1, :],
        ],
        axis=0,
    )

    bg = np.median(border, axis=0)
    dist = np.sqrt(((arr - bg) ** 2).sum(axis=2))
    mask = dist > tol

    if not mask.any():
        return img

    coords = np.argwhere(mask)
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1

    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(arr.shape[1], x1 + pad)
    y1 = min(arr.shape[0], y1 + pad)

    return img.crop((x0, y0, x1, y1))


def image_data_uri(filename: str, *, max_width: int = 220, crop_white: bool = True) -> str | None:
    """
    Lê uma imagem de /assets e devolve um data URI (imagem embutida em texto).
    """
    path = asset_path(filename)
    if not path.exists():
        return None

    img = Image.open(path)

    if crop_white:
        img = _crop_uniform_border(img)

    w, h = img.size
    if w > max_width:
        new_h = max(1, int(h * (max_width / w)))
        img = img.resize((max_width, new_h), Image.LANCZOS)

    buf = io.BytesIO()
    is_png = filename.lower().endswith(".png")
    fmt = "PNG" if is_png else "JPEG"

    if fmt == "JPEG" and img.mode != "RGB":
        img = img.convert("RGB")

    img.save(buf, format=fmt, optimize=True)

    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = "png" if fmt == "PNG" else "jpeg"
    return f"data:image/{mime};base64,{b64}"


def page_link_with_icon(
    page_path: str,
    label: str,
    *,
    icon: str = SIMULADOR_ICON,
    group_width: int | None = None,
    icon_px: int | None = None,
) -> None:
    """
    Link interno com ícone Material nativo.
    group_width/icon_px ficam aqui só para compatibilidade com chamadas antigas.
    """
    width = group_width if isinstance(group_width, int) else "content"
    st.page_link(
        page_path,
        label=label,
        icon=icon,
        width=width,
    )