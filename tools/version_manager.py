#!/usr/bin/env python3
"""版本管理器（朋友版）
备份、回滚和列出朋友 Skill 的历史版本。

Usage:
    python3 version_manager.py --action <backup|rollback|list> --slug <slug> --base-dir <path> [--version <version>]
"""

import argparse
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime


def backup_version(base_dir: str, slug: str):
    """备份当前版本"""
    skill_dir = os.path.join(base_dir, slug)
    if not os.path.isdir(skill_dir):
        print(f"错误：Skill 目录不存在 {skill_dir}", file=sys.stderr)
        sys.exit(1)

    # 读取当前版本号
    meta_path = os.path.join(skill_dir, 'meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    current_version = meta.get('version', 'v1')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    version_dir = os.path.join(skill_dir, 'versions', f'{current_version}_{timestamp}')

    os.makedirs(version_dir, exist_ok=True)

    # 备份关键文件
    files_to_backup = ['memory.md', 'persona.md', 'SKILL.md', 'meta.json']
    for fname in files_to_backup:
        src = os.path.join(skill_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(version_dir, fname))

    print(f"已备份版本 {current_version} → {version_dir}")


def rollback_version(base_dir: str, slug: str, version: str):
    """回滚到指定版本"""
    skill_dir = os.path.join(base_dir, slug)
    if not os.path.isdir(skill_dir):
        print(f"错误：Skill 目录不存在 {skill_dir}", file=sys.stderr)
        sys.exit(1)

    # 先备份当前版本
    backup_version(base_dir, slug)

    # 查找目标版本目录
    versions_dir = os.path.join(skill_dir, 'versions')
    if not os.path.isdir(versions_dir):
        print("错误：没有历史版本", file=sys.stderr)
        sys.exit(1)

    target_dir = None
    for d in os.listdir(versions_dir):
        if d.startswith(version + '_'):
            target_dir = os.path.join(versions_dir, d)
            break

    if not target_dir or not os.path.isdir(target_dir):
        print(f"错误：版本 {version} 不存在", file=sys.stderr)
        print(f"可用版本：")
        list_versions(base_dir, slug)
        sys.exit(1)

    # 恢复文件
    files_to_restore = ['memory.md', 'persona.md', 'SKILL.md', 'meta.json']
    for fname in files_to_restore:
        src = os.path.join(target_dir, fname)
        dst = os.path.join(skill_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    print(f"已回滚到版本 {version}（来自 {target_dir}）")


def list_versions(base_dir: str, slug: str):
    """列出所有历史版本"""
    versions_dir = os.path.join(base_dir, slug, 'versions')
    if not os.path.isdir(versions_dir):
        print("没有历史版本。")
        return

    versions = sorted(os.listdir(versions_dir), reverse=True)
    if not versions:
        print("没有历史版本。")
        return

    print(f"共 {len(versions)} 个历史版本：\n")
    for v in versions:
        # 格式：v1_20240115_203045
        parts = v.split('_')
        version = parts[0] if parts else v
        timestamp = '_'.join(parts[1:]) if len(parts) > 1 else ''
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                time_str = timestamp
        else:
            time_str = ''

        print(f"  {version}  —  {time_str}")


def main():
    parser = argparse.ArgumentParser(description='版本管理器（朋友版）')
    parser.add_argument('--action', required=True, choices=['backup', 'rollback', 'list'])
    parser.add_argument('--slug', required=True, help='朋友代号')
    parser.add_argument('--base-dir', default='./friends', help='基础目录')
    parser.add_argument('--version', help='目标版本号（用于 rollback）')

    args = parser.parse_args()

    if args.action == 'backup':
        backup_version(args.base_dir, args.slug)
    elif args.action == 'rollback':
        if not args.version:
            print("错误：rollback 需要 --version 参数", file=sys.stderr)
            sys.exit(1)
        rollback_version(args.base_dir, args.slug, args.version)
    elif args.action == 'list':
        list_versions(args.base_dir, args.slug)


if __name__ == '__main__':
    main()
