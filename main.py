import os
import time
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

# 获取项目根目录并添加到Python路径
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.logic_component import WX_ASR


class AudioProcessorGUI:
    def __init__(self):
        """初始化GUI界面"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("音频处理与语音识别系统")
        self.root.geometry("1000x900")  # 设置窗口大小

        # 设置窗口样式
        self.style = ttk.Style()

        # 配置标题、副标题和按钮的字体样式
        self.style.configure("Title.TLabel", font=("Microsoft YaHei UI", 24, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 14))
        self.style.configure("Action.TButton", font=("Microsoft YaHei UI", 12))

        # 设置主题色
        self.root.configure(bg="#f0f0f0")  # 设置背景色
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabelframe", background="#f0f0f0")

        # 初始化语音识别模块
        self.wxasr = WX_ASR()
        # 设置GUI组件
        self.setup_gui()

    def setup_gui(self):
        """设置GUI界面组件"""
        # 创建主框架并添加内边距
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题部分
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        ttk.Label(
            title_frame, text="音频处理与语音识别系统", style="Title.TLabel"
        ).pack()

        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20)
        )

        # 文件选择部分
        ttk.Label(control_frame, text="输入文件:", style="Subtitle.TLabel").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.input_path_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.input_path_var, width=70).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(
            control_frame,
            text="选择文件",
            style="Action.TButton",
            command=self.select_input_file,
        ).grid(row=0, column=2, padx=5)

        # 参数控制部分
        params_frame = ttk.Frame(control_frame)
        params_frame.grid(row=1, column=0, columnspan=3, pady=10)

        # 噪声控制
        noise_frame = ttk.LabelFrame(params_frame, text="噪声级别", padding="5")
        noise_frame.grid(row=0, column=0, padx=10)
        self.noise_level = ttk.Scale(
            noise_frame, from_=0.0, to=0.1, orient=tk.HORIZONTAL, length=200
        )
        self.noise_level.set(0.003)
        self.noise_level.grid(row=0, column=0, padx=5)
        self.noise_label = ttk.Label(noise_frame, text="0.3%")
        self.noise_label.grid(row=1, column=0)
        self.noise_level.configure(
            command=lambda v: self.noise_label.configure(text=f"{float(v)*100:.1f}%")
        )

        # 音量控制
        volume_frame = ttk.LabelFrame(params_frame, text="音量增益", padding="5")
        volume_frame.grid(row=0, column=1, padx=10)
        self.volume_gain = ttk.Scale(
            volume_frame, from_=0.1, to=5.0, orient=tk.HORIZONTAL, length=200
        )
        self.volume_gain.set(1.2)
        self.volume_gain.grid(row=0, column=0, padx=5)
        self.volume_label = ttk.Label(volume_frame, text="120%")
        self.volume_label.grid(row=1, column=0)
        self.volume_gain.configure(
            command=lambda v: self.volume_label.configure(text=f"{float(v)*100:.1f}%")
        )

        # 按钮框架
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)

        # 处理按钮
        ttk.Button(
            button_frame,
            text="处理音频",
            style="Action.TButton",
            command=self.process_audio,
        ).grid(row=0, column=0, padx=10)

        # 重置按钮
        ttk.Button(
            button_frame,
            text="重置",
            style="Action.TButton",
            command=self.reset_all,
        ).grid(row=0, column=1, padx=10)

        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="识别结果", padding="15")
        result_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # 设置文本框样式
        text_style = {
            "font": ("Microsoft YaHei UI", 12),
            "wrap": tk.WORD,
            "padx": 8,
            "pady": 8,
        }

        # 更新Entry控件字体
        entry_style = {"font": ("Microsoft YaHei UI", 12)}  # 增大输入框字体
        ttk.Entry(
            control_frame, textvariable=self.input_path_var, width=60, **entry_style
        ).grid(row=0, column=1, padx=5)

        # 原始音频结果
        ttk.Label(result_frame, text="原始音频识别:", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W
        )
        self.original_text = scrolledtext.ScrolledText(
            result_frame, height=5, width=100, **text_style
        )
        self.original_text.grid(row=1, column=0, pady=(0, 10))

        # 处理后音频结果
        ttk.Label(result_frame, text="处理后音频识别:", style="Subtitle.TLabel").grid(
            row=2, column=0, sticky=tk.W
        )
        self.modified_text = scrolledtext.ScrolledText(
            result_frame, height=5, width=100, **text_style
        )
        self.modified_text.grid(row=3, column=0, pady=(0, 10))

        # 比较结果
        ttk.Label(result_frame, text="文本比较结果:", style="Subtitle.TLabel").grid(
            row=4, column=0, sticky=tk.W
        )
        self.comparison_text = scrolledtext.ScrolledText(
            result_frame, height=8, width=100, **text_style
        )
        self.comparison_text.grid(row=5, column=0, pady=(0, 10))

        # 状态栏
        self.status_var = tk.StringVar()
        status_label = ttk.Label(
            main_frame, textvariable=self.status_var, style="Subtitle.TLabel"
        )
        status_label.grid(row=3, column=0, columnspan=3, pady=10)

    def select_input_file(self):
        file_path = filedialog.askopenfilename(
            title="选择音频/视频文件",
            filetypes=[
                (
                    "所有支持的格式",
                    "*.wav *.mp3 *.m4a *.aac *.ogg *.flac *.wma *.aiff *.mp4 *.avi *.mkv *.mov",
                ),
                ("视频文件", "*.mp4 *.avi *.mkv *.mov"),
                ("音频文件", "*.wav *.mp3 *.m4a *.aac *.ogg *.flac *.wma *.aiff"),
                ("所有文件", "*.*"),
            ],
        )
        if file_path:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                messagebox.showerror("错误", "所选文件不存在")
                return

            # 检查文件大小
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
            if file_size > 100:  # 限制100MB
                messagebox.showerror("错误", "文件大小超过100MB，请选择更小的文件")
                return

            # 检查是否为视频文件
            if file_path.lower().endswith((".mp4", ".avi", ".mkv", ".mov")):
                try:
                    self.status_var.set("[...] 正在处理视频...")

                    # 创建临时和输出目录
                    temp_dir = ROOT_DIR / "media" / "temp"
                    output_dir = ROOT_DIR / "media" / "output"
                    os.makedirs(temp_dir, exist_ok=True)
                    os.makedirs(output_dir, exist_ok=True)

                    # 生成临时音频文件路径
                    temp_audio = temp_dir / f"temp_audio_{int(time.time())}.wav"

                    # 提取音频
                    import moviepy.editor as mp

                    video = mp.VideoFileClip(file_path)
                    video.audio.write_audiofile(str(temp_audio))
                    video.close()

                    # 修改音频
                    modified_audio, sr = WX_ASR.modify_audio(
                        file_path=str(temp_audio),
                        output_path=str(temp_audio),
                        noise_level=0.02,
                        volume_gain=0.8,
                    )

                    # 生成输出视频路径
                    output_video = output_dir / f"modified_video_{int(time.time())}.mp4"

                    # 替换视频音频
                    WX_ASR.modify_video_audio(
                        file_path, str(temp_audio), str(output_video)
                    )

                    self.status_var.set("[√] 视频处理成功")
                    self.input_path_var.set(str(output_video))

                except Exception as e:
                    messagebox.showerror("错误", f"处理视频失败: {str(e)}")
                    return

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

                # 比较转录结果
                transcription_file = (
                    ROOT_DIR / "media" / "transcribe" / "transcription.txt"
                )
                if transcription_file.exists():
                    comparison = self.wxasr.compare_transcriptions(
                        str(transcription_file)
                    )
                    self.comparison_text.delete(1.0, tk.END)
                    self.format_comparison_result(comparison)

        except Exception as e:
            self.status_var.set(f"[x] 错误: {str(e)}")
            messagebox.showerror("错误", str(e))

    def format_comparison_result(self, result):
        if "错误" in result:
            self.comparison_text.insert(tk.END, f"[x] {result['错误']}")
            return

        comparison = result["比较结果"]
        self.comparison_text.insert(tk.END, "=== 文本比较分析报告 ===\n\n")

        # 相似度分析
        self.comparison_text.insert(tk.END, "【相似度分析】\n")
        self.comparison_text.insert(
            tk.END, f"├─ 相似度: {comparison['相似度分析']['百分比']}\n"
        )
        self.comparison_text.insert(
            tk.END, f"├─ 相同字符: {comparison['相似度分析']['相同字符数']}\n"
        )
        self.comparison_text.insert(
            tk.END, f"└─ 总字符数: {comparison['相似度分析']['总字符数']}\n\n"
        )

        # 文本统计
        self.comparison_text.insert(tk.END, "【文本统计】\n")
        self.comparison_text.insert(
            tk.END, f"├─ 原始长度: {comparison['文本统计']['原始文本长度']}\n"
        )
        self.comparison_text.insert(
            tk.END, f"├─ 测试长度: {comparison['文本统计']['测试文本长度']}\n"
        )
        self.comparison_text.insert(
            tk.END, f"└─ 长度差异: {comparison['文本统计']['长度差异']}\n"
        )

    def reset_all(self):
        # Reset input file
        self.input_path_var.set("")

        # Reset sliders to default values
        self.noise_level.set(0.05)  # 5%
        self.volume_gain.set(0.5)  # 50%

        # Clear all text areas
        self.original_text.delete(1.0, tk.END)
        self.modified_text.delete(1.0, tk.END)
        self.comparison_text.delete(1.0, tk.END)

        # Reset status
        self.status_var.set("")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AudioProcessorGUI()
    app.run()
