#!/usr/bin/env python3
# encoding=utf-8
"""
Author: Dodotry
Date: 2026-04-11 01:09:42
LastEditors: Dodotry
LastEditTime: 2026-04-11 21:58:35
"""
import csv
import xlsxwriter
from loguru import logger
import PySimpleGUI as sg

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import queue
import threading



# ===================== 全局配置 =====================
sg.theme("LightGrey1")
sg.set_options(font=("微软雅黑", 12), element_padding=(10, 5))


log_queue: queue.Queue = queue.Queue(maxsize=1000)  # 日志队列

log_event = threading.Event()  # 日志更新事件
stop_event = threading.Event()  # 停止事件
exceutor = ThreadPoolExecutor(max_workers=4)  # 线程池


# Loguru 日志配置
logger.remove()
log_buffer: sg.Multiline = None

window: sg.Window = None


def log_handler(msg):
    try:
        log_queue.put_nowait(msg.strip())
        log_event.set()  # 触发日志更新事件
    except queue.Full:
        try:
            log_queue.get_nowait()  # 丢弃最旧的日志
            log_queue.put_nowait(msg.strip())
            log_event.set()
        except:
            pass


logger.add(log_handler, format="{time:HH:mm:ss} | {level: <5} | {message}")

list_files =  lambda d : sorted(Path(d).rglob("*.csv"))

# ===================== 界面布局 =====================
def make_layout():
    layout = [
        [
            sg.Text("⚡ CSV 批量转 Excel 工具", font=("微软雅黑", 12, "bold")),
            sg.Push(),
        ],
        [sg.HorizontalSeparator(pad=(10, 5))],
        [
            sg.Push(),
            sg.Text("源目录（自动遍历CSV）：", size=(20, 1)),
            sg.Input(key="-SRC-", size=(50, 1)),
            sg.FolderBrowse("选择", button_color=("white", "#002ccc")),
            # sg.Push(),
        ],
        [
            sg.Push(),
            sg.Text("保存目录（不填则同目录）：", size=(20, 1)),
            sg.Input(key="-SAVE-", size=(50, 1)),
            sg.FolderBrowse("选择", button_color=("white", "#002ccc")),
            # sg.Push(),
        ],
        # [sg.HorizontalSeparator(pad=(10, 10))],
        [
            sg.Push(),
            sg.Button(
                "▶ 开始转换",
                key="-RUN-",
                size=(10, 1),
                button_color=("white", "#002ccc"),
            ),
            sg.Button("🧹 清空日志", size=(10, 1), button_color=("white", "#E63723")),
            sg.Button(
                "❌ 退出", size=(10, 1), button_color=("white", "#E63723"), pad=(10, 5)
            ),
        ],
        [sg.HorizontalSeparator(pad=(10, 5))],
        [sg.Text("📜 运行日志", font=("微软雅黑", 11, "bold"))],
        [
            sg.Push(),
            sg.Multiline(
                size=(100, 100),
                key="-LOG-",
                autoscroll=True,
                disabled=False,
                background_color="#fff",
                text_color="#222",
                font=("Consolas", 10),
                expand_x=True,
                pad=(6, 3),
            ),
            sg.Push(),
        ],
    ]
    return layout


# ===================== 极速转换核心 =====================
def csv2excel_fast(csv_path, xlsx_path):

    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            workbook = xlsxwriter.Workbook(xlsx_path)
            sheet = workbook.add_worksheet("Sheet1")
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#4472c4",
                    "font_name": "微软雅黑",
                    "font_size": 10,
                    "font_color": "white",
                    "border": 1,
                }
            )
            cell_format = workbook.add_format(
                {
                    "font_name": "微软雅黑",
                    "font_size": 10,
                    "border": 1,
                    "valign": "center",
                    "num_format": "#,##0.00000000",
                }
            )
            headers = next(reader)

            for col_idx, header in enumerate(headers):
                sheet.write(0, col_idx, header, header_format)
                sheet.set_column(col_idx, col_idx, 20)  # 设置列宽

            row_idx = 1
            for row in reader:
                sheet.write_row(row_idx, 0, row, cell_format)
                row_idx += 1

            workbook.close()
        return True
    except UnicodeDecodeError:
        # 兼容中文编码
        try:
            with open(csv_path, "r", encoding="gbk", newline="") as f:
                reader = csv.reader(f)
                workbook = xlsxwriter.Workbook(xlsx_path)
                sheet = workbook.add_worksheet("Sheet1")
                header_format = workbook.add_format(
                    {
                        "bold": True,
                        "bg_color": "#4472c4",
                        "font_name": "微软雅黑",
                        "font_size": 10,
                        "font_color": "white",
                        "border": 1,
                    }
                )
                cell_format = workbook.add_format(
                    {
                        "font_name": "微软雅黑",
                        "font_size": 10,
                        "border": 1,
                        "valign": "center",
                        "num_format": "#,##0.00000000",
                    }
                )
                headers = next(reader)

                for col_idx, header in enumerate(headers):
                    sheet.write(0, col_idx, header, header_format)
                    sheet.set_column(col_idx, col_idx, 20)  # 设置列宽

                row_idx = 1
                for row in reader:
                    sheet.write_row(row_idx, 0, row, cell_format)
                    row_idx += 1

                workbook.close()
            return True
        except Exception as e:
            logger.error(f"编码错误: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"写入失败: {str(e)}")
        return False


def convert_all(src_dir, save_dir):
    if not Path(src_dir).exists():
        logger.error("源目录不存在")
        return

    files = list_files(src_dir)
    if not files:
        logger.warning("未找到CSV文件")
        return

    logger.info(f"找到 {len(files)} 个CSV，开始极速转换...")

    ok = 0
    for fn in files:
        xlsx_file = fn.stem + ".xlsx"
        out_dir = fn.parent if not save_dir.strip() else Path(save_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        save_file = out_dir / xlsx_file

        logger.info(f"转换中: {fn}")
        if csv2excel_fast(fn, save_file):
            logger.success(f"✅ 完成: {fn} → {save_file}")
            ok += 1
        else:
            logger.error(f"❌ 失败: {fn}")

    logger.info(f"✅ 全部完成：成功 {ok}/{len(files)}")


# ===================== 主程序 =====================
def main():
    global window
    window = sg.Window("CSV2Excel", make_layout(), size=(800, 600), resizable=False)

    while True:

        if log_event.is_set():
            new_logs = []
            while not log_queue.empty():
                try:
                    new_logs.append(log_queue.get_nowait())
                except queue.Empty:
                    break

            current_text = window["-LOG-"].get()
            current_lines = current_text.splitlines() if current_text else []
            all_lines = current_lines + new_logs
            if len(all_lines) > 500:
                all_lines = all_lines[-500:]  # 保留最新的500行
            window["-LOG-"].update("\n".join(all_lines))
            window["-LOG-"].set_vscroll_position(1.0)  #
            log_event.clear()

        event,values = window.read(timeout=50)

        # 退出
        if event in (sg.WIN_CLOSED, "❌ 退出"):
            break

        # 清空日志
        if event == "🧹 清空日志":
            window["-LOG-"].update("")

            while not log_queue.empty():
                try:
                    log_queue.get_nowait()
                except queue.Empty:
                    break
            log_event.clear()
            continue

        # 开始转换（执行时禁用按钮）
        if event == "-RUN-":
            src = values["-SRC-"].strip()
            save = values["-SAVE-"].strip()

            if not src:
                logger.error("请选择源目录")
                continue

            # ===================== 禁用按钮 =====================
            window["-RUN-"].update(
                disabled=True, text="转换中...", button_color=("white", "#999999")
            )
            window.refresh()  # 立即刷新界面

            def run_conversion():
                try:
                    logger.info("🚀 开始批量转换")
                    convert_all(src, save)
                except Exception as e:
                    logger.error(f"转换过程中发生错误: {str(e)}")
                finally:
                    window.write_event_value("-CONMERT_DONE-", None)  # 触发转换完成事件
            exceutor.submit(run_conversion)
        
        if event == "-CONMERT_DONE-":
            # ===================== 恢复按钮 =====================
            window["-RUN-"].update(
                disabled=False, text="▶ 开始转换", button_color=("white", "#002ccc")
            )
            logger.success("🎉 转换任务完成！")
            window.refresh()  # 立即刷新界面

    stop_event.set()  # 触发停止事件
    exceutor.shutdown(wait=True)  # 关闭线程池
    window.close()


if __name__ == "__main__":
    main()
