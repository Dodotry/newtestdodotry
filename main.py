#!/usr/bin/env python3
# encoding=utf-8
"""
Author: Dodotry
Date: 2026-01-11 19:29:58
LastEditors: Dodotry
LastEditTime: 2026-01-17 20:35:03
"""
import flet as ft
import subprocess
import os
import asyncio
from pathlib import Path
import threading
import time
import sys
from assets import loadwin


env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"
WORK_DIR = Path(sys.argv[0]).parent

async def main(page: ft.Page):
    """
    FFmpeg视频剪辑工具的主函数
    """
    page.title = "FFmpeg视频剪辑工具"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    # page.scroll = ft.ScrollMode.AUTO
    page.window_width = 900
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600
    page.theme = ft.Theme(color_scheme=ft.ColorScheme(primary=ft.Colors.RED_800))
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # # --- 启动画面控件 ---
    # 1. 加载画面 (Logo + 文本)
    loading_view = ft.Column(
        [
            ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.RED_900, size=100),
            ft.Text("正在加载中...", size=20),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    # 状态引用
    input_file = ft.Ref(ft.TextField())
    output_dir_path = ft.Ref(ft.TextField())
    log_output = ft.Ref(ft.Text)()

    def add_log(message: str):
        current_log = log_output.current.value or ""
        new_log = f"{current_log}\n{message}" if current_log else message
        # 限制日志长度，保留最后2000个字符
        log_output.current.value = new_log[-2000:]
        page.update()

    def start_editing():
        """
        开始剪辑
        """
        # 禁用按钮，显示进度条
        edit_button.disabled = True
        edit_button.content = "处理中..."
        edit_button.style = ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_800,
            shape=ft.RoundedRectangleBorder(radius=10),
        )
        edit_button.update()
        progress_bar.visible = True
        progress_bar.value = 0
        status_text.value = "正在准备..."
        page.update()

        # 在后台线程中运行FFmpeg
        thread = threading.Thread(target=run_ffmpeg_command, daemon=True)
        thread.start()

    # 文件选择器
    async def pick_input_file(e):
        add_log("正在选择源文件...")
        file_path = await ft.FilePicker().pick_files(
            allowed_extensions=[
                "mp4",
                "avi",
                "mov",
                "mkv",
                "webm",
                "flv",
                "wmv",
                "m4v",
                "mpg",
                "mpeg",
            ],
            dialog_title="选择视频文件",
        )
        if file_path:
            input_file.current.value = file_path[0].path
            add_log(f"已选择源文件： {input_file.current.value}")
            input_file.current.update()
            if not output_dir_path.current.value:
                output_dir_path.current.value = str(
                    Path(input_file.current.value).parent
                )
                output_dir_path.current.update()
                add_log(f"自动设置导出目录为: {output_dir_path.current.value}")
        else:
            add_log("取消选择源文件")

    async def pick_output_dir(e):
        add_log("正在配置导出目录...")
        directory_path = await ft.FilePicker().get_directory_path(
            dialog_title="选择导出目录"
        )
        if directory_path:
            output_dir_path.current.value = directory_path
            add_log(f"已选择导出目录: {output_dir_path.current.value}")
            output_dir_path.current.update()
            # page.update()
        else:
            add_log("取消配置导出目录")

    # UI组件
    input_file_field = ft.TextField(
        label="视频源文件",
        ref=input_file,
        # width=600,
        height=50,
        text_size=12,
        border_color=ft.Colors.RED_800,
        read_only=True,
        expand=True,
        prefix_icon=ft.Icons.VIDEO_FILE,
    )

    output_dir_path_field = ft.TextField(
        label="导出目录",
        ref=output_dir_path,
        # width=600,
        height=50,
        text_size=14,
        border_color=ft.Colors.RED_800,
        read_only=True,
        expand=True,
        prefix_icon=ft.Icons.FOLDER,
    )

    # 进度和状态组件
    progress_bar = ft.ProgressBar(
        width=300, height=20, color=ft.Colors.RED_800, value=0,
        expand=True
    )
    status_text = ft.Text("就绪", size=14, color=ft.Colors.RED_800)
    progress_row = ft.Row(
        [
            status_text,
            progress_bar,
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=10,
        expand=True,
    )

    # 时间输入框
    start_time_field = ft.TextField(
        label="开始时间",
        value="00:00:00",
        # width=200,
        height=40,
        text_size=14,
        hint_text="HH:MM:SS",
        border_color=ft.Colors.RED_800,
        prefix_icon=ft.Icons.ACCESS_TIME,
        expand=True,
    )

    end_time_field = ft.TextField(
        label="结束时间",
        value="00:01:00",
        # width=200,
        height=40,
        text_size=14,
        hint_text="HH:MM:SS",
        border_color=ft.Colors.RED_800,
        prefix_icon=ft.Icons.ACCESS_TIME,
        expand=True,
    )

    # 分辨率选项
    resolution_dropdown = ft.Dropdown(
        label="分辨率",
        width=320,
        # height=50,
        text_size=14,
        border_radius=20,
        content_padding=ft.Padding(10, 5, 10, 5),
        border_color=ft.Colors.RED_800,
        options=[
            ft.dropdown.Option("720P"),
            ft.dropdown.Option("1080P"),
            ft.dropdown.Option("2K"),
        ],
        value="1080P",
    )

    # 创建剪辑按钮
    edit_button = ft.Button(
        "开始剪辑",
        on_click=start_editing,
        icon=ft.Icons.EDIT,
        width=140,
        height=40,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

    # 创建选择文件按钮
    select_file_button = ft.Button(
        "选择文件",
        icon=ft.Icons.VIDEO_FILE,
        width=140,
        height=40,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=pick_input_file,
    )

    # 创建选择目录按钮
    select_dir_button = ft.Button(
        "导出目录",
        on_click=pick_output_dir,
        icon=ft.Icons.FOLDER,
        width=140,
        height=40,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )

    log_list = ft.ListView(
        [
            ft.Text(
                ref=log_output,
                value="等待开始...",
                size=12,
                font_family="monospace",
                selectable=True,
            )
        ],
        expand=True,
        padding=10,
        spacing=5,
    )
    # 日志显示容器
    log_container = ft.Container(
        content=log_list,
        padding=0,
        border=ft.Border.all(width=1, color=ft.Colors.GREY_300),  # 使用最新 API
        border_radius=5,
        expand=True,  # 拉伸填充
        bgcolor=ft.Colors.GREY_100,
    )

    # 日志标题和内容
    log_display = ft.Column(
        [
            ft.Row(
                [
                    ft.Text(
                        "执行信息", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_800
                    ),
                    progress_row,
                ],
                # alignment=ft.MainAxisAlignment.START,
            ),
            log_container,
        ],
        expand=True,  # 拉伸填充
        spacing=5,
    )

    def validate_time_format(time_str):
        """
        验证时间格式 HH:MM:SS
        """
        try:
            parts = time_str.split(":")
            if len(parts) != 3:
                return False
            h, m, s = map(int, parts)
            if h < 0 or m < 0 or s < 0:
                return False
            if m > 59 or s > 59:
                return False
            return True
        except:
            return False

    def time_to_seconds(time_str):
        """
        将时间字符串转换为秒数
        """
        h, m, s = time_str.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)

    def get_resolution_dimensions(res):
        """
        获取分辨率对应的尺寸
        """
        resolutions = {"720P": "1280x720", "1080P": "1920x1080", "2K": "2560x1440"}
        return resolutions.get(res, "1920x1080")

    def update_progress(progress_value, message, is_error=False):
        """
        更新进度条和状态
        """
        progress_bar.value = progress_value
        status_text.value = message
        if is_error:
            status_text.color = ft.Colors.RED_700
        else:
            status_text.color = ft.Colors.GREEN_700
        progress_bar.update()
        # page.update()

    def reset_edit_button():
        """
        重置编辑按钮状态
        """
        edit_button.disabled = False
        edit_button.content = "开始剪辑"
        edit_button.style = ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN,
            shape=ft.RoundedRectangleBorder(radius=10),
        )
        edit_button.update()

    def run_ffmpeg_command():
        """
        在后台线程中运行FFmpeg命令
        """
        # nonlocal input_file,output_dir_path
        input_file_path = input_file.current.value.strip()
        output_path_str = output_dir_path.current.value.strip()
        try:
            # 验证输入
            if not input_file_path:
                add_log("❌错误： 请选择视频源文件")
                reset_edit_button()
                return

            if not output_path_str:
                add_log("❌错误： 请设置导出目录")
                reset_edit_button()
                return

            if not validate_time_format(start_time_field.value):
                add_log("❌错误： 开始时间格式错误，请使用 HH:MM:SS 格式")
                reset_edit_button()
                return

            if not validate_time_format(end_time_field.value):
                add_log("❌错误： 结束时间格式错误，请使用 HH:MM:SS 格式")
                reset_edit_button()
                return

            start_seconds = time_to_seconds(start_time_field.value)
            end_seconds = time_to_seconds(end_time_field.value)

            if start_seconds >= end_seconds:
                add_log("❌错误： 开始时间必须早于结束时间")
                reset_edit_button()
                return

            # 检查文件是否存在
            if not os.path.exists(input_file_path):
                add_log(f"❌错误： 文件 '{input_file_path}' 不存在")
                reset_edit_button()
                return

            # 检查导出目录是否存在
            if not os.path.exists(output_path_str):
                try:
                    os.makedirs(output_path_str)
                except Exception as e:
                    add_log(f"❌错误： 无法创建导出目录: {str(e)}")
                    reset_edit_button()
                    return

            # 准备导出文件名
            input_path = Path(input_file_path)
            output_filename = f"{input_path.stem}_剪辑_{time.strftime('%Y%m%d_%H%M%S')}{input_path.suffix}"
            output_path = Path(output_path_str) / output_filename

            # 构建FFmpeg命令
            cmd = [
                f"{WORK_DIR/'ffmpeg.exe'}",
                "-i",
                input_file_path,
                "-ss",
                start_time_field.value,
                "-to",
                end_time_field.value,
                "-vf",
                f"scale={get_resolution_dimensions(resolution_dropdown.value)}",
                "-c:a",
                "copy",
                "-y",  # 覆盖导出文件
                str(output_path),
            ]

            update_progress(0.3, "处理中...")
            add_log("正在处理视频...")

            # 执行FFmpeg命令
            try:
                # 在Windows上使用CREATE_NO_WINDOW标志，避免弹出控制台窗口
                creation_flags = 0
                if sys.platform == "win32":
                    creation_flags = subprocess.CREATE_NO_WINDOW

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    creationflags=creation_flags,
                    env=env,
                    encoding="utf-8",
                )
            except FileNotFoundError:
                update_progress(
                    0, "❌： 未找到FFmpeg", True
                )
                add_log("❌错误： 未找到FFmpeg，请确保已安装并添加到系统PATH")
                reset_edit_button()
                return

            if result.returncode == 0:
                update_progress(1.0, f"✅剪辑成功： {output_filename}")
                add_log(f"✅剪辑完成： {output_filename}")
            else:
                error_msg = result.stderr[:200] if result.stderr else "未知错误"
                update_progress(0, f"❌： {error_msg}", True)
                add_log(f"❌剪辑失败： {error_msg}")

        except Exception as ex:
            update_progress(0, f"❌执行错误： {str(ex)}", True)
            add_log(f"❌执行错误： {str(ex)}")
            reset_edit_button()
        finally:
            # 重置按钮状态
            reset_edit_button()
            # edit_button.update()
            progress_bar.value = 1
            page.update()

    # 使用说明
    instructions_container = ft.Container(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE_700),
                        ft.Text(
                            "使用说明",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.RED_800,
                        ),
                    ]
                ),
                ft.Divider(height=5),
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    size=12,
                                    color=ft.Colors.GREEN_600,
                                ),
                                ft.Text(
                                    "选择要剪辑的视频文件（支持mp4, avi, mov, mkv, webm, flv, wmv等格式）",
                                    size=12,
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    size=12,
                                    color=ft.Colors.GREEN_600,
                                ),
                                ft.Text(
                                    "设置导出目录",
                                    size=12,
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    size=12,
                                    color=ft.Colors.GREEN_600,
                                ),
                                ft.Text(
                                    "选择导出分辨率（720P, 1080P, 2K）",
                                    size=12,
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    size=12,
                                    color=ft.Colors.GREEN_600,
                                ),
                                ft.Text(
                                    "设置剪辑的开始和结束时间（格式: 时:分:秒）",
                                    size=12,
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    size=12,
                                    color=ft.Colors.GREEN_600,
                                ),
                                ft.Text("点击开始剪辑按钮", size=12),
                            ]
                        ),
                    ],
                    spacing=5,
                ),
                # ft.Divider(height=5),
                ft.Container(
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.WARNING,
                                size=12,
                                color=ft.Colors.ORANGE_700,
                            ),
                            ft.Text(
                                "注意: 请确保系统已安装FFmpeg并已添加到PATH环境变量",
                                size=12,
                                color=ft.Colors.ORANGE_700,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]
                    ),
                    padding=ft.Padding.only(top=10),
                ),
            ]
        ),
        padding=20,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=10,
    )

    main_content = ft.Column(
        [   instructions_container,
            ft.Row(
                [
                    input_file_field,
                    select_file_button,
                    output_dir_path_field,
                    select_dir_button,
                ],
                spacing=5,
            ),
            ft.Row(
                [
                    resolution_dropdown,
                    start_time_field,
                    end_time_field,
                    edit_button,
                ],
                # expand=True,
                spacing=20,
                # alignment=ft.MainAxisAlignment.END,
            ),
            # progress_row,
            log_display,
        ],
        expand=True,
        spacing=15,
    )

    # 3. 使用 AnimatedSwitcher 来管理切换
    switcher = ft.AnimatedSwitcher(
        loading_view,
        transition=ft.AnimatedSwitcherTransition.FADE,  # 淡入淡出和缩放切换
        duration=500,  # 切换动画持续时间
        # scale=0.8,  # 初始缩放比例
        align=ft.Alignment.CENTER,
        expand=True,
    )
    page.add(switcher)
    page.update()  # 确保加载画面先绘制
    await asyncio.sleep(0.5)
    # 构建UI布局
    switcher.content = main_content
    page.update()
    # page.add(
    #     # ft.Text(
    #     #     "FFmpeg视频剪辑工具",
    #     #     size=28,
    #     #     weight=ft.FontWeight.BOLD,
    #     #     color=ft.Colors.BLUE_900,
    #     # ),
    #     instructions_container,
    #     main_content,
    # )


# 应用入口
if __name__ == "__main__":
    ft.run(main)
    # try:
    #     import pyi_splash
    #     pyi_splash.close()
    # except ImportError:
    #     pass
