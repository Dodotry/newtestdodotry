#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-04-18 15:31:57
LastEditors: Dodotry
LastEditTime: 2026-04-18 15:53:26
'''
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import pandas as pd
import textwrap
import os

# 全局设置
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# 配置文件路径
CONFIG_PATH = "app_config.json"
DATA_PATH = "table_data.xlsx"

class MultiTabApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 加载窗口大小和位置
        self.load_window_geometry()

        self.title("CustomTkinter 完整多标签页界面（含保存/导出）")
        
        # 设置窗口图标（替换为你自己的.ico路径）
        try:
            self.iconbitmap("app.ico")  # 有图标就用这个
        except:
            pass

        # ========== 创建标签页容器 ==========
        self.tabview = ctk.CTkTabview(self, width=880, height=560)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

        # 新建标签
        self.tab_form = self.tabview.add("表单录入")
        self.tab_table = self.tabview.add("数据表格")
        self.tab_scroll = self.tabview.add("滚动内容")
        self.tab_setting = self.tabview.add("系统设置")

        # 默认选中第一个
        self.tabview.set("表单录入")

        # 调整标签页居左对齐
        self.tabview._segmented_button.grid(sticky="W")

        # ========== 初始化数据 ==========
        self.table_data = []

        # ========== 构建各个标签页 ==========
        self.build_form_tab()
        self.build_table_tab()
        self.build_scroll_tab()
        self.build_setting_tab()

        # 关闭窗口时保存大小位置
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ===================== 窗口记忆大小 =====================
    def load_window_geometry(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                geo = config.get("window_geometry", "900x600")
                self.geometry(geo)
        except:
            self.geometry("900x600")

    def save_window_geometry(self):
        config = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        config["window_geometry"] = self.geometry()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def on_close(self):
        self.save_window_geometry()
        self.destroy()

    # ===================== 表单标签页 =====================
    def build_form_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_form, width=820, height=480)
        frame.pack(padx=15, pady=15, fill="both", expand=True)

        ctk.CTkLabel(frame, text="用户信息录入", font=("", 22, "bold")).pack(pady=10)

        # 第一行：姓名、年龄、电话
        row1_frame = ctk.CTkFrame(frame)
        row1_frame.pack(fill="x", padx=20, pady=(10, 0))
        row1_frame.grid_columnconfigure((1, 3, 5), weight=1)

        ctk.CTkLabel(row1_frame, text="姓名：").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_name = ctk.CTkEntry(row1_frame, placeholder_text="请输入姓名")
        self.entry_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(row1_frame, text="年龄：").grid(row=0, column=2, padx=15, pady=5, sticky="w")
        self.entry_age = ctk.CTkEntry(row1_frame, placeholder_text="请输入年龄")
        self.entry_age.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(row1_frame, text="电话：").grid(row=0, column=4, padx=15, pady=5, sticky="w")
        self.entry_phone = ctk.CTkEntry(row1_frame, placeholder_text="请输入电话")
        self.entry_phone.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        # 第二行：下拉选择框
        row2_frame = ctk.CTkFrame(frame)
        row2_frame.pack(fill="x", padx=20, pady=(10, 0))
        row2_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(row2_frame, text="性别：").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_gender = ctk.CTkComboBox(row2_frame, values=["男", "女", "保密"])
        self.combo_gender.set("男")
        self.combo_gender.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(row2_frame, text="状态：").grid(row=0, column=2, padx=15, pady=5, sticky="w")
        self.combo_status = ctk.CTkComboBox(row2_frame, values=["正常", "禁用"])
        self.combo_status.set("正常")
        self.combo_status.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(frame, text="备注信息：").pack(anchor="w", padx=20, pady=(10, 0))
        self.text_note = ctk.CTkTextbox(frame, height=100)
        self.text_note.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(
            frame, text="提交并添加到表格", fg_color="#2E8B57", hover_color="#277548",
            command=self.on_form_submit
        ).pack(pady=10)

        ctk.CTkButton(
            frame, text="保存表单到JSON", fg_color="#587E9B", hover_color="#466983",
            command=self.save_form_to_json
        ).pack(pady=5)

    def on_form_submit(self):
        name = self.entry_name.get().strip()
        age = self.entry_age.get().strip()
        gender = self.combo_gender.get()
        phone = self.entry_phone.get().strip()
        status = self.combo_status.get()
        note = self.text_note.get("0.0", "end").strip()

        if not name:
            messagebox.showwarning("提示", "请输入姓名")
            return

        # 添加到表格
        self.tree.insert("", "end", values=(name, age, gender, phone, status))
        self.table_data.append([name, age, gender, phone, status])
        messagebox.showinfo("成功", "已添加到表格")

    def save_form_to_json(self):
        data = {
            "name": self.entry_name.get().strip(),
            "age": self.entry_age.get().strip(),
            "gender": self.combo_gender.get(),
            "phone": self.entry_phone.get().strip(),
            "status": self.combo_status.get(),
            "note": self.text_note.get("0.0", "end").strip()
        }
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"表单已保存到：\n{path}")

    # ===================== 表格标签页 =====================
    def build_table_tab(self):
        frame = ctk.CTkFrame(self.tab_table)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("", 11, "bold"))
        style.configure("Treeview", rowheight=25, font=("", 10))

        scroll_y = ttk.Scrollbar(frame)
        scroll_y.pack(side="right", fill="y")

        columns = ("name", "age", "gender", "phone", "status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree.yview)

        self.tree.heading("name", text="姓名")
        self.tree.heading("age", text="年龄")
        self.tree.heading("gender", text="性别")
        self.tree.heading("phone", text="电话")
        self.tree.heading("status", text="状态")

        self.tree.column("name", width=120)
        self.tree.column("age", width=80)
        self.tree.column("gender", width=80)
        self.tree.column("phone", width=150)
        self.tree.column("status", width=100)

        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # 按钮栏
        btn_frame = ctk.CTkFrame(self.tab_table)
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(btn_frame, text="导出Excel", width=120, command=self.export_table_excel).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="导出JSON", width=120, command=self.export_table_json).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="删除选中", width=120, fg_color="#c70000", hover_color="#a00000", command=self.delete_selected_row).pack(side="left", padx=10)

    def delete_selected_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一行")
            return
        for item in selected:
            self.tree.delete(item)
        messagebox.showinfo("成功", "已删除选中行")

    def export_table_json(self):
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            data.append({
                "姓名": values[0],
                "年龄": values[1],
                "性别": values[2],
                "电话": values[3],
                "状态": values[4]
            })
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"表格已导出JSON：\n{path}")

    def export_table_excel(self):
        data = []
        for item in self.tree.get_children():
            data.append(self.tree.item(item)["values"])
        df = pd.DataFrame(data, columns=["姓名", "年龄", "性别", "电话", "状态"])
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if path:
            df.to_excel(path, index=False)
            messagebox.showinfo("成功", f"表格已导出Excel：\n{path}")

    # ===================== 滚动内容标签页 =====================
    def build_scroll_tab(self):
        scroll_frame = ctk.CTkScrollableFrame(self.tab_scroll, width=820, height=480)
        scroll_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(scroll_frame, text="长文本 + 多组件滚动演示", font=("", 20, "bold")).pack(pady=10)

        long_text = textwrap.dedent("""
        这是一个很长的内容区域，用于演示滚动条功能。
        
        CustomTkinter 提供了 CTkScrollableFrame，可以直接实现带滚动条的面板，
        内部可以放任意组件：标签、按钮、输入框、图片、表格等。
        
        当内容高度超过窗口时，自动出现垂直滚动条，非常适合展示大量配置项、日志、说明文档等场景。
        """)

        ctk.CTkLabel(scroll_frame, text=long_text, wraplength=780, justify="left").pack(anchor="w", padx=10, pady=10)

        for i in range(1, 21):
            ctk.CTkLabel(scroll_frame, text=f"滚动内容条目 {i} —— 配置/日志/列表").pack(anchor="w", padx=20, pady=5)
            ctk.CTkProgressBar(scroll_frame).pack(fill="x", padx=20, pady=(0, 10))

    # ===================== 系统设置标签页 =====================
    def build_setting_tab(self):
        frame = ctk.CTkFrame(self.tab_setting)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="系统设置", font=("", 22, "bold")).pack(pady=15)

        ctk.CTkSwitch(frame, text="跟随系统主题", command=lambda: ctk.set_appearance_mode("system")).pack(anchor="w", padx=30, pady=10)
        ctk.CTkSwitch(frame, text="强制深色模式", command=lambda: ctk.set_appearance_mode("dark")).pack(anchor="w", padx=30, pady=10)
        ctk.CTkSwitch(frame, text="强制浅色模式", command=lambda: ctk.set_appearance_mode("light")).pack(anchor="w", padx=30, pady=10)

        ctk.CTkFrame(frame, height=2, fg_color="gray").pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(frame, text="界面缩放比例：").pack(anchor="w", padx=30, pady=(10, 0))
        self.slider_scale = ctk.CTkSlider(frame, from_=0.8, to=1.5, number_of_steps=7)
        self.slider_scale.set(1.0)
        self.slider_scale.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(frame, text="自动保存间隔：").pack(anchor="w", padx=30, pady=(10, 0))
        self.slider_save = ctk.CTkSlider(frame, from_=1, to=10, number_of_steps=9)
        self.slider_save.set(5)
        self.slider_save.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkButton(frame, text="保存所有设置", fg_color="#1f6aa5", hover_color="#145587", command=self.save_all_settings).pack(pady=20)

    def save_all_settings(self):
        config = {
            "appearance_mode": ctk.get_appearance_mode(),
            "scale": self.slider_scale.get(),
            "auto_save_interval": self.slider_save.get(),
            "window_geometry": self.geometry()
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("成功", "所有设置已保存到 app_config.json")

if __name__ == "__main__":
    app = MultiTabApp()
    app.mainloop()