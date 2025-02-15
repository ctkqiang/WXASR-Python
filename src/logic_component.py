import librosa
import numpy as np
import os
import soundfile as sf
import speech_recognition as sr
from typing import Optional, Union, Tuple


class WX_ASR:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()

    @staticmethod
    def modify_audio(
        file_path: str,
        output_path: str,
        noise_level: float = 0.005,
        volume_gain: float = 1.0,
    ) -> Tuple[np.ndarray, int]:
        """
        修改音频文件，添加噪声并调整音量。

        参数:
            file_path (str): 输入音频文件路径
            output_path (str): 保存修改后音频的路径
            noise_level (float): 要添加的噪声量 (默认: 0.005)
            volume_gain (float): 音量调整系数 (默认: 1.0)

        返回:
            Tuple[np.ndarray, int]: 修改后的音频数组和采样率

        异常:
            FileNotFoundError: 如果输入文件不存在
            ValueError: 如果音频文件无法处理
        """
        try:
            # 加载音频文件
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"[x] 找不到音频文件: {file_path}")

            audio, sr = librosa.load(file_path, sr=None)

            # 应用音频转换
            noise = np.random.normal(0, noise_level, audio.shape)
            modified_audio = (audio + noise) * volume_gain

            # 确保音频保持在有效范围内
            modified_audio = np.clip(modified_audio, -1.0, 1.0)

            # 保存修改后的音频
            sf.write(output_path, modified_audio, sr)

            return modified_audio, sr

        except Exception as e:
            raise ValueError(f"处理音频文件时出错: {str(e)}")

    def ASR_Tester(self, file_path) -> str:
        with sr.AudioFile(file_path) as source:
            audio_data = self.recognizer.record(source)

            try:
                text = self.recognizer.recognize_google(audio_data, language="zh-CN")
                return text
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(
                    f"Could not request results from Google Speech Recognition service; {e}"
                )

        return ""


if __name__ == "__main__":
    try:
        modified_audio, sr = WX_ASR.modify_audio(
            "./media/test_data/test.wav",
            "./media/output/modified_audio.wav",
            noise_level=0.003,
            volume_gain=1.2,
        )
        print(f"Audio successfully modified and saved with sample rate: {sr}Hz")
    except Exception as e:
        print(f"Error: {str(e)}")
