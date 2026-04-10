#!/usr/bin/env python3
"""照片元信息分析器（朋友版）
从照片中提取 EXIF 信息（拍摄时间、地点），建立时间线。

Usage:
    python3 photo_analyzer.py --dir <directory> --output <output_path>
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime


def analyze_photos(directory: str) -> dict:
    """分析目录中的照片"""
    image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.heic'}

    photos = []
    for root, dirs, files in os.walk(directory):
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext in image_exts:
                fpath = os.path.join(root, fname)
                stat = os.stat(fpath)
                photos.append({
                    'path': fpath,
                    'name': fname,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })

    # 按修改时间排序
    photos.sort(key=lambda x: x['modified'])

    return {
        'total': len(photos),
        'photos': photos,
    }


def extract_exif(photo_path: str) -> dict:
    """尝试提取 EXIF 信息（需要 Pillow）"""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS

        img = Image.open(photo_path)
        exif_data = img._getexif()

        if not exif_data:
            return {}

        result = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)

            if tag == 'DateTimeOriginal':
                result['date_taken'] = str(value)
            elif tag == 'GPSInfo':
                gps = {}
                for gps_tag_id in value:
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps[gps_tag] = value[gps_tag_id]
                if 'GPSLatitude' in gps and 'GPSLongitude' in gps:
                    lat = convert_to_degrees(gps['GPSLatitude'])
                    lon = convert_to_degrees(gps['GPSLongitude'])
                    if gps.get('GPSLatitudeRef', 'N') == 'S':
                        lat = -lat
                    if gps.get('GPSLongitudeRef', 'E') == 'W':
                        lon = -lon
                    result['latitude'] = lat
                    result['longitude'] = lon

        return result
    except ImportError:
        return {'error': 'Pillow 未安装，无法提取 EXIF'}
    except Exception as e:
        return {'error': str(e)}


def convert_to_degrees(value):
    """将 GPS 坐标转换为十进制"""
    d, m, s = value
    return d + m / 60.0 + s / 3600.0


def main():
    parser = argparse.ArgumentParser(description='照片元信息分析器（朋友版）')
    parser.add_argument('--dir', required=True, help='照片目录')
    parser.add_argument('--output', required=True, help='输出文件路径')

    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"错误：目录不存在 {args.dir}", file=sys.stderr)
        sys.exit(1)

    result = analyze_photos(args.dir)

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(f"# 照片分析报告\n\n")
        f.write(f"扫描目录：{args.dir}\n")
        f.write(f"照片总数：{result['total']}\n\n")

        if result['photos']:
            f.write("## 照片时间线\n\n")
            for photo in result['photos']:
                size_kb = photo['size'] / 1024
                f.write(f"- **{photo['name']}** ({size_kb:.0f}KB) — 修改时间：{photo['modified']}\n")

                # 尝试提取 EXIF
                exif = extract_exif(photo['path'])
                if exif.get('date_taken'):
                    f.write(f"  - 拍摄时间：{exif['date_taken']}\n")
                if exif.get('latitude'):
                    f.write(f"  - GPS：{exif['latitude']:.4f}, {exif['longitude']:.4f}\n")
                if exif.get('error') and 'Pillow' in exif['error']:
                    f.write(f"  - {exif['error']}\n")
        else:
            f.write("未找到照片文件。\n")

    print(f"分析完成，结果已写入 {args.output}")


if __name__ == '__main__':
    main()
