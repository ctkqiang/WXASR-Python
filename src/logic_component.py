import os
import time
import random
import whisper
import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
import speech_recognition as sr
from funasr import AutoModel
from typing import Optional, Union, Tuple
from deprecated import deprecated

isTesting: bool = True


class WX_ASR:
    def __init__(self) -> None:
        self.language: str = "zh"
        self.funasr_model: str = (
            "damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
        )
        self.recognizer: sr.Recognizer = sr.Recognizer()
        """
        模型选择：Whisper提供多种模型（base基础型、small、medium、large）。
        较大的模型提供更高的准确性，但需要更多的计算资源。
        """
        self.model: whisper.Whisper = whisper.load_model("base")

    @staticmethod
    def modify_audio(
        file_path: str,
        output_path: str,
        noise_level: float = 0.05,
        volume_gain: float = 0.5,
    ) -> Tuple[np.ndarray, int]:
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"[x] 未找到音频文件：{file_path}")

            audio, sr = librosa.load(file_path, sr=None)

            # 添加高频噪声 (超出人耳范围但影响ASR)
            t = np.linspace(0, len(audio) / sr, len(audio))
            high_freq_noise = np.sin(2 * np.pi * 18000 * t) * 0.1
            audio = audio + high_freq_noise

            # 添加微小时间偏移
            shift_samples = int(sr * 0.001)  # 1ms shift
            audio = np.roll(audio, shift_samples)

            # 应用音量增益
            audio = audio * volume_gain

            # 添加选择性频率调制
            mod_freq = 50  # 50Hz modulation
            modulation = 1 + 0.1 * np.sin(2 * np.pi * mod_freq * t)
            audio = audio * modulation

            # 限制在有效范围内
            modified_audio = np.clip(audio, -1.0, 1.0)

            # 保存修改后的音频
            sf.write(output_path, modified_audio, sr)

            return modified_audio, sr

        except Exception as e:
            raise ValueError(f"[x] 处理音频文件时出错：{str(e)}")

    def ASR_Tester(self, file_path: str) -> str:
        try:
            result = self.model.transcribe(file_path, language=self.language)
            text = result["text"]

            # 检查转录结果是否为空
            if not text or text.strip() == "":
                return "[x] 无法转录音频"

            # 如果转录目录不存在则创建
            output_dir = Path(__file__).parent.parent / "media" / "transcribe"
            output_dir.mkdir(parents=True, exist_ok=True)

            # 创建输出文件
            output_file = output_dir / f"transcription.txt"

            # 将转录文本写入文件
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"[√] 转录文本已保存至: {output_file}")
            return text
        except Exception as e:
            print(f"[x] 语音识别转录失败: {e}")
            return str(e)
        return None

    def calculate_repetition_rate(self, text: str) -> dict:
        """
        计算文本中的重复率
        参数:
            text (str): 需要分析的文本
        返回:
            dict: 包含重复率分析结果的字典
        """
        try:
            # 分词处理
            words = text.split()
            total_words = len(words)

            # 统计词频
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1

            # 计算重复词数量
            repeated_words = sum(count - 1 for count in word_freq.values() if count > 1)

            # 计算重复率
            repetition_rate = (
                (repeated_words / total_words * 100) if total_words > 0 else 0
            )

            # 找出重复次数最多的词
            most_repeated = sorted(
                [(word, count) for word, count in word_freq.items() if count > 1],
                key=lambda x: x[1],
                reverse=True,
            )[
                :5
            ]  # 只显示前5个

            return {
                "重复率分析": {
                    "总字数": total_words,
                    "重复字数": repeated_words,
                    "重复率": f"{repetition_rate:.2f}%",
                    "高频重复词": [
                        {"词": word, "出现次数": count} for word, count in most_repeated
                    ],
                }
            }

        except Exception as e:
            return {"错误": f"计算重复率时出错: {str(e)}"}

    def compare_transcriptions(self, transcription_file: str) -> dict:
        try:
            # 获取原始参考文本路径
            original_file = (
                Path(__file__).parent.parent
                / "media"
                / "transcribe"
                / "original_transcription.txt"
            )

            # 读取文件内容
            with open(original_file, "r", encoding="utf-8") as f1, open(
                transcription_file, "r", encoding="utf-8"
            ) as f2:
                original_text = f1.read().strip()
                test_text = f2.read().strip()

            # 计算文本相似度
            total_chars = max(len(original_text), len(test_text))
            if total_chars == 0:
                similarity = 0
            else:
                same_chars = sum(1 for a, b in zip(original_text, test_text) if a == b)
                similarity = (same_chars / total_chars) * 100

            # 添加重复率分析
            original_repetition = self.calculate_repetition_rate(original_text)
            test_repetition = self.calculate_repetition_rate(test_text)

            return {
                "比较结果": {
                    "相似度分析": {
                        "百分比": f"{similarity:.2f}%",
                        "相同字符数": same_chars,
                        "总字符数": total_chars,
                    },
                    "文本统计": {
                        "原始文本长度": len(original_text),
                        "测试文本长度": len(test_text),
                        "长度差异": abs(len(original_text) - len(test_text)),
                    },
                    "重复率分析": {
                        "原始文本": original_repetition["重复率分析"],
                        "测试文本": test_repetition["重复率分析"],
                    },
                    "文本内容": {
                        "原始文本": original_text,
                        "测试文本": test_text,
                    },
                }
            }

        except Exception as e:
            print(f"[x] 比较文件时出错: {str(e)}")
            return {"错误": f"比较文件时出错: {str(e)}"}

    def print_comparison(self, result: dict) -> None:
        if "错误" in result:
            print(f"\n[x] {result['错误']}")
            return

        comparison = result["比较结果"]
        print("\n=== 文本比较分析报告 ===")
        print("\n【相似度分析】")
        print(f"├─ 相似度: {comparison['相似度分析']['百分比']}")
        print(f"├─ 相同字符: {comparison['相似度分析']['相同字符数']}")
        print(
            f"└─ 总字符数: {comparison['相似度分析']['总字符数']}"
        )  # Fixed: removed extra 's'

        print("\n【文本统计】")
        print(f"├─ 原始长度: {comparison['文本统计']['原始文本长度']}")
        print(f"├─ 测试长度: {comparison['文本统计']['测试文本长度']}")
        print(f"└─ 长度差异: {comparison['文本统计']['长度差异']}")

        print("\n【文本内容】")
        print(f"├─ 原始文本: {comparison['文本内容']['原始文本']}")
        print(f"└─ 测试文本: {comparison['文本内容']['测试文本']}")
        print("\n【重复率分析】")
        print("├─ 原始文本:")
        print(f"│  ├─ 重复率: {comparison['重复率分析']['原始文本']['重复率']}")
        print(f"│  ├─ 总字数: {comparison['重复率分析']['原始文本']['总字数']}")
        print(f"│  └─ 重复字数: {comparison['重复率分析']['原始文本']['重复字数']}")
        print("└─ 测试文本:")
        print(f"   ├─ 重复率: {comparison['重复率分析']['测试文本']['重复率']}")
        print(f"   ├─ 总字数: {comparison['重复率分析']['测试文本']['总字数']}")
        print(f"   └─ 重复字数: {comparison['重复率分析']['测试文本']['重复字数']}")

        print("\n===================\n")

    @deprecated("由于未知原因导致的多个错误，此方法已弃用，请使用 ASR_Tester 方法代替")
    def transcribe_audio_with_funasr(self, file_path: str) -> str:
        try:
            model = AutoModel(
                disable_update=True, model=self.funasr_model, model_revision="v1.2.4"
            )
            result = model.transcribe(file_path)
            return result["text"]
        except Exception as e:
            raise ValueError(f"[x] 转录过程中出错：{str(e)}")

    def get_subtitle_repetition_rate(self, transcription_file: str):
        """
        获取字幕重复率

        参数:
            transcription_file (str): 需要比较的转录文本文件路径

        返回:
            str: 字幕重复率，以百分比形式呈现
        """
        result = self.compare_transcriptions(transcription_file)
        if "错误" in result:
            return f"Error: {result['错误']}"
        return result["比较结果"]["相似度分析"]["百分比"]


if __name__ == "__main__":
    if isTesting:
        try:
            ROOT_DIR = Path(__file__).parent.parent
            test_audio = ROOT_DIR / "media" / "test_data" / "test.wav"

            wx = WX_ASR()

            # 测试[1]：测试音频修改功能
            print("\n=== 音频修改测试 ===")
            try:
                # Create output directory if it doesn't exist
                output_dir = ROOT_DIR / "media" / "output"
                output_dir.mkdir(parents=True, exist_ok=True)

                modified_audio_path = output_dir / f"modified_audio_20250216_170115.wav"
                modified_audio, sr = wx.modify_audio(
                    file_path=str(test_audio),
                    output_path=str(modified_audio_path),
                    noise_level=0.02,
                    volume_gain=0.8,
                )
                print(f"[√] 音频已修改并保存至: {modified_audio_path}")
                print(f"[√] 采样率: {sr}")
                print(f"[√] 修改后音频形状: {modified_audio.shape}")
            except Exception as e:
                print(f"[x] 音频修改失败: {e}")

            # 测试[2]：测试语音识别和字幕重复率分析
            print("\n=== 语音识别测试 ===")
            try:
                # 测试原始音频转录
                print("\n转录原始音频:")
                original_text = wx.ASR_Tester(str(test_audio))
                print(f"[√] 原始音频转录结果: {original_text}")

                # 分析原始音频字幕重复率
                original_repetition = wx.calculate_repetition_rate(original_text)
                print("\n原始音频字幕重复率分析:")
                print(f"├─ 总字数: {original_repetition['重复率分析']['总字数']}")
                print(f"├─ 重复字数: {original_repetition['重复率分析']['重复字数']}")
                print(f"└─ 重复率: {original_repetition['重复率分析']['重复率']}")

                # 测试修改后的音频转录
                print("\n转录修改后的音频:")
                modified_text = wx.ASR_Tester(str(modified_audio_path))
                print(f"[√] 修改后音频转录结果: {modified_text}")

                # 分析修改后音频字幕重复率
                modified_repetition = wx.calculate_repetition_rate(modified_text)
                print("\n修改后音频字幕重复率分析:")
                print(f"├─ 总字数: {modified_repetition['重复率分析']['总字数']}")
                print(f"├─ 重复字数: {modified_repetition['重复率分析']['重复字数']}")
                print(f"└─ 重复率: {modified_repetition['重复率分析']['重复率']}")

                # 保存转录结果以供比较
                transcribe_dir = ROOT_DIR / "media" / "transcribe"
                transcribe_dir.mkdir(parents=True, exist_ok=True)

                with open(
                    transcribe_dir / "original_transcription.txt", "w", encoding="utf-8"
                ) as f:
                    f.write(original_text)
                with open(
                    transcribe_dir / "transcription.txt", "w", encoding="utf-8"
                ) as f:
                    f.write(modified_text)

                # 比较转录结果
                result = wx.compare_transcriptions(
                    str(transcribe_dir / "transcription.txt")
                )
                wx.print_comparison(result)

                repetition_rate = wx.get_subtitle_repetition_rate(
                    str(transcribe_dir / "transcription.txt")
                )

                print("\n=== 字幕重复率总结 ===")
                print(f"├─ 相似度: {repetition_rate}")
                print(
                    "└─ 状态: "
                    + (
                        "✓ 正常"
                        if float(repetition_rate.strip("%")) > 80
                        else "⚠️ 需要优化"
                    )
                )
                print("=====================\n")
            except Exception as e:
                print(f"[x] {e}")
        except Exception as e:
            print(f"[x] 错误: {str(e)}")
    else:
        pass
