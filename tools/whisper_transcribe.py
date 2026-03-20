#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
本地 Whisper 语音识别工具
完全自动化：视频 → 文字稿
"""

import sys
import os
import subprocess
import whisper
import json

def extract_audio(video_path, audio_path):
    """从视频提取音频"""
    print(f"从视频提取音频：{video_path} → {audio_path}")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "libmp3lame", "-ab", "128k",
        "-y", audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffmpeg 错误：{result.stderr}")
        return False
    print(f"✅ 音频提取成功：{audio_path}")
    return True

def transcribe_audio(audio_path, model_size="base", language="zh"):
    """使用 Whisper 识别语音"""
    print(f"加载 Whisper 模型：{model_size}")
    model = whisper.load_model(model_size)
    
    print(f"开始识别：{audio_path}")
    result = model.transcribe(audio_path, language=language)
    
    return result

def main(video_path, output_path=None, model_size="base"):
    """主流程"""
    print("="*60)
    print("Whisper 本地语音识别")
    print("="*60)
    
    # 检查文件
    if not os.path.exists(video_path):
        print(f"❌ 文件不存在：{video_path}")
        return None
    
    # 生成临时音频路径
    base_name = os.path.splitext(video_path)[0]
    audio_path = f"{base_name}.mp3"
    
    # 1. 提取音频
    if video_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        if not extract_audio(video_path, audio_path):
            return None
    else:
        audio_path = video_path  # 已经是音频文件
    
    # 2. 语音识别
    print("\n开始语音识别...")
    result = transcribe_audio(audio_path, model_size, "zh")
    
    # 3. 输出结果
    full_text = result.get("text", "").strip()
    
    print("\n" + "="*60)
    print("📝 识别文字稿:")
    print("="*60)
    print(full_text)
    print("="*60)
    
    # 4. 保存结果
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"\n✅ 文字稿已保存：{output_path}")
    
    # 保存详细结果（JSON）
    json_path = f"{base_name}_result.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ 详细结果已保存：{json_path}")
    
    # 清理临时音频
    if audio_path != video_path and os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"🗑️  已清理临时文件：{audio_path}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3.8 whisper_transcribe.py <视频文件路径> [输出文件路径] [模型大小]")
        print("模型大小：tiny, base, small, medium, large (默认：base)")
        print("示例：python3.8 whisper_transcribe.py video.mp4")
        print("      python3.8 whisper_transcribe.py video.mp4 output.txt small")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    model_size = sys.argv[3] if len(sys.argv) > 3 else "base"
    
    result = main(video_path, output_path, model_size)
    
    if result:
        print("\n" + "="*60)
        print("✅ 完成！")
        print("="*60)
