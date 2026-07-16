#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
competitor-researcher / doctor.py

ワークショップ前・利用前の環境チェック。標準ライブラリのみで動作し、
何も変更しない（読み取りのみ）。常に終了コード 0 で終わる。

使い方:
    python3 doctor.py [作業フォルダ（省略時はカレントディレクトリ）]

チェック内容:
  1. Python のバージョン
  2. PDF化用ブラウザ（Chrome / Edge / Chromium / Brave）の有無
  3. 作業フォルダ（自社サービス.md / reports/）の有無
  4. 自社サービス.md が記入済みかどうか（簡易判定）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from html_to_pdf import find_browser  # noqa: E402


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    target = os.path.abspath(target)

    ok, warn = [], []

    # 1. Python
    v = sys.version_info
    if v >= (3, 6):
        ok.append("Python %d.%d — OK" % (v.major, v.minor))
    else:
        warn.append("Python が古すぎます（%d.%d）。3.6 以上を推奨します。" % (v.major, v.minor))

    # 2. PDF化用ブラウザ
    browser = find_browser()
    if browser:
        ok.append("PDF化用ブラウザ — OK（%s）" % os.path.basename(browser))
    else:
        warn.append("PDF化用ブラウザ（Chrome/Edge）が見つかりません。"
                    "PDFは自動スキップされますが、.html をブラウザで開いて"
                    "「印刷 → PDFとして保存」で代用できます。")

    # 3. 作業フォルダ
    profile = os.path.join(target, "自社サービス.md")
    reports = os.path.join(target, "reports")
    if os.path.isfile(profile) and os.path.isdir(reports):
        ok.append("作業フォルダ — OK（%s）" % target)
    else:
        warn.append("このフォルダは作業スペースではないようです（自社サービス.md / reports/ が"
                    "見つかりません）。/competitor-researcher:init を実行してください。")

    # 4. 自社サービス.md の記入状況（簡易判定）
    if os.path.isfile(profile):
        try:
            with open(profile, encoding="utf-8") as f:
                body = f.read()
            if body.count("（例:") >= 4:
                warn.append("自社サービス.md がテンプレートのままのようです。"
                            "分かるところだけ記入するか、サンプル_自社サービス.md の内容を"
                            "コピーしてください（未記入でも調査時に質問されるので動きます）。")
            else:
                ok.append("自社サービス.md — 記入済みのようです")
        except OSError:
            warn.append("自社サービス.md を読み取れませんでした。")

    print("=== 専属リサーチャー 環境チェック ===")
    for line in ok:
        print("  ✅ %s" % line)
    for line in warn:
        print("  ⚠️  %s" % line)
    print()
    if warn:
        print("総合: 要確認 %d 件（⚠️ の案内に従ってください。Web検索の可否は Claude Code 側で確認します）" % len(warn))
    else:
        print("総合: 準備OK（Web検索の可否は Claude Code 側で確認します）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
