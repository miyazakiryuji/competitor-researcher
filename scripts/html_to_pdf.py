#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
competitor-researcher / html_to_pdf.py

生成済みの HTML ダッシュボードを、ヘッドレスブラウザ（Chrome / Edge / Chromium / Brave）で
PDF に変換する。標準ライブラリのみで動作する。

ブラウザが見つからない場合は、分かりやすいメッセージを出して終了コード 2 で終わる
（その場合は .html をブラウザで開いて「印刷 → PDF として保存」すればよい）。

使い方:
    python3 html_to_pdf.py <input.html> [output.pdf]
    （output.pdf 省略時は input と同名の .pdf を同じ場所に作る）

終了コード: 0=成功 / 1=引数・入力エラー / 2=ブラウザ未検出 / 3=変換失敗
"""
import os
import shutil
import subprocess
import sys
from urllib.parse import urljoin
from urllib.request import pathname2url

CANDIDATES_MAC = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]

# Windows: 環境変数のベースパス + 相対パスで探す
WIN_RELATIVE = [
    os.path.join("Google", "Chrome", "Application", "chrome.exe"),
    os.path.join("Microsoft", "Edge", "Application", "msedge.exe"),
    os.path.join("Chromium", "Application", "chrome.exe"),
]

LINUX_NAMES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "microsoft-edge", "brave-browser", "chrome",
]


def find_browser():
    if sys.platform == "darwin":
        for path in CANDIDATES_MAC:
            if os.path.exists(path):
                return path
    elif os.name == "nt":
        bases = [os.environ.get(k) for k in
                 ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
        for base in bases:
            if not base:
                continue
            for rel in WIN_RELATIVE:
                path = os.path.join(base, rel)
                if os.path.exists(path):
                    return path
    for name in LINUX_NAMES:
        path = shutil.which(name)
        if path:
            return path
    return None


def main():
    if len(sys.argv) < 2:
        print("使い方: python3 html_to_pdf.py <input.html> [output.pdf]")
        return 1

    src = os.path.abspath(sys.argv[1])
    if not os.path.isfile(src):
        print("エラー: 入力ファイルが見つかりません: %s" % src)
        return 1

    if len(sys.argv) >= 3:
        out = os.path.abspath(sys.argv[2])
    else:
        out = os.path.splitext(src)[0] + ".pdf"

    browser = find_browser()
    if browser is None:
        print("PDF化用のブラウザ（Chrome / Edge / Chromium）が見つかりませんでした。")
        print("→ 手動でもPDF化できます: %s をブラウザで開き、" % os.path.basename(src))
        print("   印刷（Cmd/Ctrl+P）→「PDFとして保存」を選んでください。")
        return 2

    url = urljoin("file:", pathname2url(src))
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf=%s" % out,
        url,
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=120, check=False)
    except subprocess.TimeoutExpired:
        print("エラー: PDF変換がタイムアウトしました（120秒）。")
        return 3

    if os.path.isfile(out) and os.path.getsize(out) > 0:
        print("PDFを作成しました: %s" % out)
        return 0

    print("エラー: PDFの作成に失敗しました。")
    print("→ 手動でもPDF化できます: .html をブラウザで開き、印刷 →「PDFとして保存」。")
    return 3


if __name__ == "__main__":
    sys.exit(main())
