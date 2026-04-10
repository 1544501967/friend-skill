#!/usr/bin/env python3
"""QQ 聊天记录解析器（朋友版）
支持的输入格式：
- txt（QQ 导出的聊天记录文本）
- mht（QQ 合并转发的网页格式）

Usage:
    python3 qq_parser.py --file <path> --target <name> --output <output_path>
"""

import argparse
import re
import os
import sys
from pathlib import Path


def parse_qq_txt(file_path: str, target_name: str) -> dict:
    """解析 QQ 导出的 txt 格式

    典型格式：
    2024-01-15 20:30:45 张三(123456)
    今天好累啊
    """
    messages = []
    current_msg = None

    # QQ 时间戳 + 发送者(QQ号) 模式
    msg_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+?)(?:\(\d+\))?$')

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n')
            match = msg_pattern.match(line)
            if match:
                if current_msg:
                    messages.append(current_msg)
                timestamp, sender = match.groups()
                current_msg = {
                    'timestamp': timestamp.strip(),
                    'sender': sender.strip(),
                    'content': ''
                }
            elif current_msg and line.strip():
                if current_msg['content']:
                    current_msg['content'] += '\n'
                current_msg['content'] += line

    if current_msg:
        messages.append(current_msg)

    return analyze_qq_messages(messages, target_name)


def parse_qq_mht(file_path: str, target_name: str) -> dict:
    """解析 QQ 的 mht 格式（合并转发）

    mht 是带 HTML 的格式，需要提取文本部分
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # 简单的 HTML 标签清理
    text = re.sub(r'<[^>]+>', '\n', content)
    # 压缩多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    return {
        'target_name': target_name,
        'total_messages': 0,
        'target_messages': 0,
        'user_messages': 0,
        'raw_text': text[:50000],  # 限制大小
        'analysis': {
            'note': 'mht 格式已提取纯文本，需要人工辅助分析'
        },
        'sample_messages': []
    }


def analyze_qq_messages(messages: list, target_name: str) -> dict:
    """分析 QQ 消息列表"""
    target_msgs = [m for m in messages if target_name in m.get('sender', '')]
    user_msgs = [m for m in messages if target_name not in m.get('sender', '')]

    all_target_text = ' '.join([m['content'] for m in target_msgs if m.get('content')])
    msg_lengths = [len(m['content']) for m in target_msgs if m.get('content')]
    avg_length = sum(msg_lengths) / len(msg_lengths) if msg_lengths else 0

    return {
        'target_name': target_name,
        'total_messages': len(messages),
        'target_messages': len(target_msgs),
        'user_messages': len(user_msgs),
        'analysis': {
            'avg_message_length': round(avg_length, 1),
            'message_style': 'short_burst' if avg_length < 20 else 'long_form',
        },
        'sample_messages': [m['content'] for m in target_msgs[:50] if m.get('content')],
    }


def main():
    parser = argparse.ArgumentParser(description='QQ 聊天记录解析器（朋友版）')
    parser.add_argument('--file', required=True, help='输入文件路径')
    parser.add_argument('--target', required=True, help='朋友的名字/昵称')
    parser.add_argument('--output', required=True, help='输出文件路径')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"错误：文件不存在 {args.file}", file=sys.stderr)
        sys.exit(1)

    ext = Path(args.file).suffix.lower()
    if ext == '.mht':
        result = parse_qq_mht(args.file, args.target)
    else:
        result = parse_qq_txt(args.file, args.target)

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(f"# QQ 聊天记录分析 — {args.target}\n\n")
        f.write(f"来源文件：{args.file}\n")
        f.write(f"总消息数：{result.get('total_messages', 'N/A')}\n")
        f.write(f"ta的消息数：{result.get('target_messages', 'N/A')}\n\n")

        analysis = result.get('analysis', {})
        f.write(f"## 消息风格\n")
        f.write(f"- 平均消息长度：{analysis.get('avg_message_length', 'N/A')} 字\n")
        f.write(f"- 风格：{'短句连发型' if analysis.get('message_style') == 'short_burst' else '长段落型'}\n\n")

        if result.get('sample_messages'):
            f.write("## 消息样本（前50条）\n")
            for i, msg in enumerate(result['sample_messages'], 1):
                f.write(f"{i}. {msg}\n")

        if result.get('raw_text'):
            f.write("\n## 原始文本\n")
            f.write(result['raw_text'])

    print(f"分析完成，结果已写入 {args.output}")


if __name__ == '__main__':
    main()
