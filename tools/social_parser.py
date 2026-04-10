#!/usr/bin/env python3
"""社交媒体内容解析器（朋友版）
扫描目录中的社交媒体截图和文件，分类并生成报告。

Usage:
    python3 social_parser.py --dir <directory> --output <output_path>
"""

import argparse
import os
import sys
from pathlib import Path


def scan_directory(directory: str) -> dict:
    """扫描目录，分类文件"""
    image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    text_exts = {'.txt', '.md', '.csv', '.json'}

    images = []
    texts = []
    others = []

    for root, dirs, files in os.walk(directory):
        for fname in files:
            fpath = os.path.join(root, fname)
            ext = Path(fname).suffix.lower()

            if ext in image_exts:
                images.append(fpath)
            elif ext in text_exts:
                texts.append(fpath)
            else:
                others.append(fpath)

    return {
        'images': sorted(images),
        'texts': sorted(texts),
        'others': sorted(others),
    }


def read_text_files(text_paths: list) -> str:
    """读取文本文件内容"""
    contents = []
    for path in text_paths:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            contents.append(f"### {os.path.basename(path)}\n\n{content}")
        except Exception as e:
            contents.append(f"### {os.path.basename(path)}\n\n[读取失败: {e}]")
    return '\n\n---\n\n'.join(contents)


def main():
    parser = argparse.ArgumentParser(description='社交媒体内容解析器（朋友版）')
    parser.add_argument('--dir', required=True, help='社交媒体截图/文件目录')
    parser.add_argument('--output', required=True, help='输出文件路径')

    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"错误：目录不存在 {args.dir}", file=sys.stderr)
        sys.exit(1)

    result = scan_directory(args.dir)

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(f"# 社交媒体内容扫描报告\n\n")
        f.write(f"扫描目录：{args.dir}\n")
        f.write(f"图片文件：{len(result['images'])} 个\n")
        f.write(f"文本文件：{len(result['texts'])} 个\n")
        f.write(f"其他文件：{len(result['others'])} 个\n\n")

        if result['images']:
            f.write("## 图片截图（请用 Read 工具直接查看）\n\n")
            for img in result['images']:
                f.write(f"- `{img}`\n")
            f.write("\n")

        if result['texts']:
            f.write("## 文本内容\n\n")
            f.write(read_text_files(result['texts']))
            f.write("\n\n")

        if result['others']:
            f.write("## 其他文件\n\n")
            for other in result['others']:
                f.write(f"- `{other}`\n")

    print(f"扫描完成，结果已写入 {args.output}")


if __name__ == '__main__':
    main()
