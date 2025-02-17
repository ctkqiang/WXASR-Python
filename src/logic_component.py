import os
import time
import random
import whisper
import librosa
import numpy as np
import soundfile as sf
import jieba
from pathlib import Path
import speech_recognition as sr
from typing import Optional, Union, Tuple
from deprecated import deprecated

isTesting: bool = True


class WX_ASR:
    # 版本信息
    VERSION = "1.0.0"
    DEVELOPER = "钟智强"
    DEVELOPER_EMAIL = "johnmelodymel@qq.com"

    def __init__(self) -> None:
        self.language: str = "zh"
        self.recognizer: sr.Recognizer = sr.Recognizer()
        self.model: whisper.Whisper = whisper.load_model("base")

    @staticmethod
    def get_info() -> dict:
        """
        获取软件信息
        """
        return {
            "版本": WX_ASR.VERSION,
            "开发者": WX_ASR.DEVELOPER,
            "联系方式": WX_ASR.DEVELOPER_EMAIL,
            "语言支持": "中文",
            "功能": ["音频处理与变声", "语音识别转写", "文本相似度分析", "重复率计算"],
        }

    def __init__(self) -> None:
        self.language: str = "zh"
        self.recognizer: sr.Recognizer = sr.Recognizer()
        self.model: whisper.Whisper = whisper.load_model("base")

    @staticmethod
    def modify_video_audio(
        input_video: str, modified_audio: str, output_video: str
    ) -> None:
        """
        将修改后的音频替换视频中的原始音频
        """
        try:
            import moviepy.editor as mp

            # 加载视频和修改后的音频
            video = mp.VideoFileClip(input_video)
            new_audio = mp.AudioFileClip(modified_audio)

            # 替换音频
            final_video = video.set_audio(new_audio)

            # 保存新视频（保持原视频编码设置）
            final_video.write_videofile(
                output_video,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
            )

            # 清理资源
            video.close()
            new_audio.close()
            final_video.close()

        except Exception as e:
            raise ValueError(f"[x] 替换视频音频时出错：{str(e)}")

    def modify_audio(
        file_path: str,
        output_path: str,
        noise_level: float = 0.05,
        volume_gain: float = 0.5,
    ) -> Tuple[np.ndarray, int]:
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"[x] 未找到音频文件：{file_path}")

            # 加载音频文件
            audio, sr = librosa.load(file_path, sr=None)

            # 时域变换处理
            segments = np.array_split(audio, 40)  # 分段处理
            modified_segments = []

            for segment in segments:
                # 时间拉伸
                stretch_factor = np.random.uniform(0.97, 1.03)
                stretched = librosa.effects.time_stretch(segment, rate=stretch_factor)

                # 音高偏移
                pitch_shift = np.random.uniform(-1.5, 1.5)
                shifted = librosa.effects.pitch_shift(
                    stretched, sr=sr, n_steps=pitch_shift
                )

                modified_segments.append(shifted)

            # 重组音频
            audio = np.concatenate([seg for seg in modified_segments if len(seg) > 0])

            # 音量调整
            audio = audio * 0.85  # 固定音量增益

            # 添加白噪声
            white_noise = np.random.normal(0, 0.02, len(audio))
            audio = audio + white_noise

            # 标准化音频
            modified_audio = np.clip(audio, -1.0, 1.0)
            modified_audio = modified_audio / np.max(np.abs(modified_audio))

            # 保存修改后的音频
            sf.write(output_path, modified_audio, sr)

            # 复制成功的音频到输出目录
            if "temp_audio_1739713328.wav" in str(output_path):
                success_path = (
                    Path(output_path).parent.parent
                    / "output"
                    / "successful_modification.wav"
                )
                sf.write(str(success_path), modified_audio, sr)

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

            # 改进相似度计算方法
            def calculate_semantic_similarity(text1: str, text2: str) -> tuple:
                # 分词处理
                words1 = list(jieba.cut(text1))
                words2 = list(jieba.cut(text2))

                # 计算词语级别的相似度
                word_similarity = len(set(words1) & set(words2)) / len(
                    set(words1) | set(words2)
                )

                # 计算句子级别的相似度
                sentences1 = text1.split("。")
                sentences2 = text2.split("。")
                sentence_pairs = []
                for s1 in sentences1:
                    if s1.strip():
                        max_sim = max(
                            (
                                len(set(s1) & set(s2)) / len(set(s1) | set(s2))
                                if s2.strip()
                                else 0
                            )
                            for s2 in sentences2
                        )
                        sentence_pairs.append(max_sim)

                sentence_similarity = (
                    sum(sentence_pairs) / len(sentence_pairs) if sentence_pairs else 0
                )

                # 综合计算（词语相似度占40%，句子相似度占60%）
                final_similarity = word_similarity * 0.4 + sentence_similarity * 0.6
                return (
                    final_similarity * 100,
                    word_similarity * 100,
                    sentence_similarity * 100,
                )

            # 计算改进后的相似度
            similarity, word_sim, sent_sim = calculate_semantic_similarity(
                original_text, test_text
            )

            return {
                "比较结果": {
                    "相似度分析": {
                        "百分比": f"{similarity:.2f}%",
                        "相同字符数": same_chars,
                        "总字符数": total_chars,
                        "语义分析": {
                            "词语相似度": f"{word_sim:.2f}%",
                            "句子相似度": f"{sent_sim:.2f}%",
                        },
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
        print("├─ 字符级相似度:")
        print(f"│  ├─ 相同字符: {comparison['相似度分析']['相同字符数']}")
        print(f"│  └─ 总字符数: {comparison['相似度分析']['总字符数']}")
        print("├─ 语义相似度分析:")
        print(f"│  ├─ 词语相似度: {comparison['相似度分析']['语义分析']['词语相似度']}")
        print(f"│  └─ 句子相似度: {comparison['相似度分析']['语义分析']['句子相似度']}")
        print(f"└─ 综合相似度: {comparison['相似度分析']['百分比']}")

        print("\n【文本统计】")
        print(f"├─ 原始长度: {comparison['文本统计']['原始文本长度']}")
        print(f"├─ 测试长度: {comparison['文本统计']['测试文本长度']}")
        print(f"└─ 长度差异: {comparison['文本统计']['长度差异']}")

        print("\n【文本内容】")
        print(f"├─ 原始文本: {comparison['文本内容']['原始文本']}\n")
        print(f"└─ 测试文本: {comparison['文本内容']['测试文本']}\n")
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
            test_audio = (
                ROOT_DIR
                / "media"
                / "test_data"
                / "2月15🌐编程设计32 2025-02-02 下午8.19.47.mp4"
            )

            wx = WX_ASR()

            # 测试[1]：测试音频修改功能
            print("\n=== 音频修改测试 ===")
            try:
                output_dir = ROOT_DIR / "media" / "output"
                output_dir.mkdir(parents=True, exist_ok=True)

                modified_audio_path = output_dir / f"modified_audio.wav"
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

                o = wx.ASR_Tester(
                    file_path=output_dir / "modified_audio_20250216_212736.wav"
                )

                print(f"[v] {o}")
            except Exception as e:
                print(f"[x] {e}")
        except Exception as e:
            print(f"[x] 错误: {str(e)}")
    else:
        pass
