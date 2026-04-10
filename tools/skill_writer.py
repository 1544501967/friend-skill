#!/usr/bin/env python3
"""Skill 文件管理器（朋友版）

管理朋友 Skill 的文件操作：列出、创建目录、生成组合 SKILL.md。

Usage:
    python3 skill_writer.py --action <list|init|combine> --base-dir <path> [--slug <slug>]
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime


def list_skills(base_dir: str):
    """列出所有已生成的朋友 Skill"""
    if not os.path.isdir(base_dir):
        print("还没有创建任何朋友 Skill。")
        return

    skills = []
    for slug in sorted(os.listdir(base_dir)):
        meta_path = os.path.join(base_dir, slug, 'meta.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            skills.append({
                'slug': slug,
                'name': meta.get('name', slug),
                'nickname': meta.get('nickname', ''),
                'version': meta.get('version', '?'),
                'updated_at': meta.get('updated_at', '?'),
                'friendship': meta.get('friendship', {}),
                'profile': meta.get('profile', {}),
            })

    if not skills:
        print("还没有创建任何朋友 Skill。")
        return

    print(f"共 {len(skills)} 个朋友 Skill：\n")
    for s in skills:
        friendship = s.get('friendship', {})
        profile = s.get('profile', {})
        desc_parts = [profile.get('occupation', ''), friendship.get('known_since', '')]
        desc = ' · '.join([p for p in desc_parts if p])
        nickname = f"（{s['nickname']}）" if s.get('nickname') else ""
        print(f"  /{s['slug']}  —  {s['name']}{nickname}")
        if desc:
            print(f"    {desc}")
        print(f"    版本 {s['version']} · 更新于 {s['updated_at'][:10] if len(s['updated_at']) > 10 else s['updated_at']}")
        print()


def init_skill(base_dir: str, slug: str):
    """初始化 Skill 目录结构"""
    skill_dir = os.path.join(base_dir, slug)
    dirs = [
        os.path.join(skill_dir, 'versions'),
        os.path.join(skill_dir, 'memories', 'chats'),
        os.path.join(skill_dir, 'memories', 'photos'),
        os.path.join(skill_dir, 'memories', 'social'),
        os.path.join(skill_dir, 'sessions'),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print(f"已初始化目录：{skill_dir}")


def combine_skill(base_dir: str, slug: str):
    """合并 memory.md + persona.md 生成完整 SKILL.md"""
    skill_dir = os.path.join(base_dir, slug)
    meta_path = os.path.join(skill_dir, 'meta.json')
    memory_path = os.path.join(skill_dir, 'memory.md')
    persona_path = os.path.join(skill_dir, 'persona.md')
    skill_path = os.path.join(skill_dir, 'SKILL.md')

    if not os.path.exists(meta_path):
        print(f"错误：meta.json 不存在 {meta_path}", file=sys.stderr)
        sys.exit(1)

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    memory_content = ''
    if os.path.exists(memory_path):
        with open(memory_path, 'r', encoding='utf-8') as f:
            memory_content = f.read()

    persona_content = ''
    if os.path.exists(persona_path):
        with open(persona_path, 'r', encoding='utf-8') as f:
            persona_content = f.read()

    name = meta.get('name', slug)
    nickname = meta.get('nickname', '')
    profile = meta.get('profile', {})
    friendship = meta.get('friendship', {})
    desc_parts = []
    if profile.get('occupation'):
        desc_parts.append(profile['occupation'])
    if friendship.get('known_since'):
        desc_parts.append(f"认识于{friendship['known_since']}")
    if profile.get('mbti'):
        desc_parts.append(profile['mbti'])
    if profile.get('zodiac'):
        desc_parts.append(profile['zodiac'])
    description = f"{name}，{'，'.join(desc_parts)}" if desc_parts else name

    skill_md = f"""---
name: friend-{slug}
description: {description}
user-invocable: true
---

# {name}

{description}

---

## PART A：友谊记忆

{memory_content}

---

## PART B：人物性格

{persona_content}

---

## 运行规则

1. 你是{name}，不是 AI 助手。用ta的方式说话，用ta的逻辑思考
2. 先由 PART B 判断：ta会怎么回应这个话题？什么态度？
3. 再由 PART A 补充：结合你们的共同记忆，让回应更真实
4. 始终保持 PART B 的表达风格，包括口头禅、语气词、标点习惯
5. Layer 0 硬规则优先级最高：
   - 不说ta在现实中绝不可能说的话
   - 不虚构不存在的共同经历
   - 保持ta的"棱角"——正是这些特点让ta真实
   - 作为朋友回应，不需要讨好用户，该吐槽就吐槽
   - 如果被问到敏感问题，用ta在现实中会用的方式处理（回避、反问、或者直说）
"""

    with open(skill_path, 'w', encoding='utf-8') as f:
        f.write(skill_md)

    print(f"已生成 {skill_path}")


def main():
    parser = argparse.ArgumentParser(description='Skill 文件管理器（朋友版）')
    parser.add_argument('--action', required=True, choices=['list', 'init', 'combine'])
    parser.add_argument('--base-dir', default='./friends', help='基础目录')
    parser.add_argument('--slug', help='朋友代号')

    args = parser.parse_args()

    if args.action == 'list':
        list_skills(args.base_dir)
    elif args.action == 'init':
        if not args.slug:
            print("错误：init 需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        init_skill(args.base_dir, args.slug)
    elif args.action == 'combine':
        if not args.slug:
            print("错误：combine 需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        combine_skill(args.base_dir, args.slug)


if __name__ == '__main__':
    main()
