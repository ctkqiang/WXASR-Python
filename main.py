import os
import time
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# 获取项目根目录并添加到Python路径
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.logic_component import WX_ASR


class AudioProcessorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("音频处理与语音识别系统")
        self.root.geometry("800x600")

        self.wxasr = WX_ASR()
        self.setup_gui()

    def setup_gui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 音频处理部分
        ttk.Label(main_frame, text="音频处理", font=("Arial", 14, "bold")).grid(
            row=0, column=0, pady=10
        )

        # 输入文件选择
        ttk.Label(main_frame, text="输入文件:").grid(row=1, column=0, sticky=tk.W)
        self.input_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path_var, width=50).grid(
            row=1, column=1
        )
        ttk.Button(main_frame, text="选择文件", command=self.select_input_file).grid(
            row=1, column=2
        )

        # 参数设置
        ttk.Label(main_frame, text="噪声级别:").grid(row=2, column=0, sticky=tk.W)
        self.noise_level = ttk.Scale(
            main_frame, from_=0.0, to=0.1, orient=tk.HORIZONTAL
        )
        self.noise_level.set(0.003)
        self.noise_level.grid(row=2, column=1, sticky=(tk.W, tk.E))

        ttk.Label(main_frame, text="音量增益:").grid(row=3, column=0, sticky=tk.W)
        self.volume_gain = ttk.Scale(
            main_frame, from_=0.1, to=5.0, orient=tk.HORIZONTAL
        )
        self.volume_gain.set(1.2)
        self.volume_gain.grid(row=3, column=1, sticky=(tk.W, tk.E))

        # 处理按钮
        ttk.Button(main_frame, text="处理音频", command=self.process_audio).grid(
            row=4, column=0, columnspan=3, pady=10
        )

        # 语音识别部分
        ttk.Label(main_frame, text="语音识别", font=("Arial", 14, "bold")).grid(
            row=5, column=0, pady=10
        )

        # 原始音频识别结果
        ttk.Label(main_frame, text="原始音频识别结果:").grid(
            row=6, column=0, sticky=tk.W
        )
        self.original_text = tk.Text(main_frame, height=4, width=50)
        self.original_text.grid(row=6, column=1, columnspan=2)

        # 处理后音频识别结果
        ttk.Label(main_frame, text="处理后音频识别结果:").grid(
            row=7, column=0, sticky=tk.W
        )
        self.modified_text = tk.Text(main_frame, height=4, width=50)
        self.modified_text.grid(row=7, column=1, columnspan=2)

        # 状态栏
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var).grid(
            row=8, column=0, columnspan=3, pady=10
        )

    def select_input_file(self):
        file_path = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )
        if file_path:
            self.input_path_var.set(file_path)

    def process_audio(self):
        try:
            input_path = self.input_path_var.get()
            if not input_path:
                messagebox.showerror("错误", "请选择输入文件")
                return

            # 创建输出目录
            output_dir = ROOT_DIR / "media" / "output"
            os.makedirs(output_dir, exist_ok=True)

            # 生成输出文件路径
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"modified_audio_{timestamp}.wav"

            # 处理音频
            modified_audio, sr = WX_ASR.modify_audio(
                input_path,
                str(output_path),
                noise_level=self.noise_level.get(),
                volume_gain=self.volume_gain.get(),
            )

            if modified_audio is not None and modified_audio.size > 0:
                self.status_var.set(f"[√] 音频处理成功，采样率: {sr}Hz")

                # 进行语音识别
                original = self.wxasr.ASR_Tester(file_path=input_path)
                modified = self.wxasr.ASR_Tester(file_path=str(output_path))

                # 显示识别结果
                self.original_text.delete(1.0, tk.END)
                self.original_text.insert(tk.END, original or "识别失败")

                self.modified_text.delete(1.0, tk.END)
                self.modified_text.insert(tk.END, modified or "识别失败")

        except Exception as e:
            self.status_var.set(f"[x] 错误: {str(e)}")
            messagebox.showerror("错误", str(e))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AudioProcessorGUI()
    app.run()
