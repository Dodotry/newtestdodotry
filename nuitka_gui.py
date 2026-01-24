import sys
import subprocess
import threading
import queue
import os
import socket
import platform
import re
import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox, QRadioButton,
    QGroupBox, QTabWidget, QFrame, QStatusBar, QMenuBar, QMenu, 
    QListWidget, QListWidgetItem, QComboBox, QSpinBox, QFileDialog,
    QMessageBox, QScrollArea, QScroller, QSplitter, QGridLayout
)
from PySide6.QtCore import (
    QThread, Signal, QObject, QTimer, Qt, QUrl
)
from PySide6.QtGui import (
    QFont, QDesktopServices, QIcon,QAction,
)


class Worker(QObject):
    """
    工作线程类，用于执行 Nuitka 命令。
    通过信号与主线程通信。
    """
    finished = Signal(int)  # 发送进程返回码
    output_received = Signal(str)  # 发送标准输出
    error_received = Signal(str)  # 发送标准错误

    def __init__(self):
        super().__init__()
        self.proc = None
        self._is_running = False

    def run_command(self, command_list):
        """
        在工作线程中执行命令。
        """
        self._is_running = True
        try:
            # 启动子进程
            self.proc = subprocess.Popen(
                command_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )

            # 读取输出流
            while self._is_running:
                output_line = self.proc.stdout.readline()
                if output_line:
                    self.output_received.emit(output_line)

                error_line = self.proc.stderr.readline()
                if error_line:
                    self.error_received.emit(error_line)

                # 检查进程是否结束
                if self.proc.poll() is not None:
                    break

            # 读取剩余输出（如果有的话）
            remaining_out, remaining_err = self.proc.communicate()
            if remaining_out:
                self.output_received.emit(remaining_out)
            if remaining_err:
                self.error_received.emit(remaining_err)

            return_code = self.proc.returncode
            self.finished.emit(return_code)
        except Exception as e:
            self.error_received.emit(f"Error running command: {e}\n")
            self.finished.emit(-1) # 返回错误码
        finally:
            self._is_running = False

    def stop(self):
        """
        尝试停止正在运行的进程。
        """
        if self.proc and self.proc.poll() is None:
            self.proc.terminate() # 尝试优雅终止
            try:
                self.proc.wait(timeout=2) # 等待最多2秒
            except subprocess.TimeoutExpired:
                self.proc.kill() # 强制杀死
        self._is_running = False


class NuitkaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Nuitka 打包工具 (PySide6)')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # 初始化核心组件
        self.worker = Worker()
        self.thread_pool = []

        # 设置中央小部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 顶部基本信息区域 ---
        basic_info_group = QGroupBox("基础选项")
        basic_info_layout = QFormLayout(basic_info_group)

        self.script_path_edit = QLineEdit()
        self.script_path_edit.setReadOnly(True)
        btn_select_script = QPushButton("浏览脚本")
        btn_select_script.clicked.connect(self.select_script)

        script_hbox = QHBoxLayout()
        script_hbox.addWidget(self.script_path_edit)
        script_hbox.addWidget(btn_select_script)

        self.interpreter_path_edit = QLineEdit()
        self.interpreter_path_edit.setReadOnly(True)
        btn_select_interpreter = QPushButton("浏览解释器")
        btn_select_interpreter.clicked.connect(self.select_interpreter)

        interpreter_hbox = QHBoxLayout()
        interpreter_hbox.addWidget(self.interpreter_path_edit)
        interpreter_hbox.addWidget(btn_select_interpreter)

        basic_info_layout.addRow("Python 脚本路径:", script_hbox)
        basic_info_layout.addRow("Python 解释器路径:", interpreter_hbox)

        # --- 标签页区域 ---
        self.tabs = QTabWidget()

        # 添加各个标签页
        self.setup_basic_tab()
        self.setup_package_tab()
        self.setup_imports_tab()
        self.setup_onefile_tab()
        self.setup_data_tab()
        self.setup_dll_tab()
        self.setup_warn_tab()
        self.setup_run_tab()
        self.setup_compile_tab()
        self.setup_output_tab()
        self.setup_deployment_tab()
        self.setup_debug_tab()
        self.setup_c_compiler_tab()
        self.setup_os_tab()
        self.setup_info_tab()
        self.setup_plugin_tab()

        # --- 控制台和命令显示区域 ---
        console_splitter = QSplitter(Qt.Vertical)
        
        command_group = QGroupBox("构建命令")
        command_layout = QVBoxLayout(command_group)
        self.command_display = QTextEdit()
        self.command_display.setMaximumHeight(100) # 限制高度
        command_layout.addWidget(self.command_display)

        console_group = QGroupBox("打包控制台")
        console_layout = QVBoxLayout(console_group)
        self.console_display = QTextEdit()
        self.console_display.setReadOnly(True)
        console_layout.addWidget(self.console_display)

        console_splitter.addWidget(command_group)
        console_splitter.addWidget(console_group)
        console_splitter.setSizes([100, 500]) # 初始大小比例

        # --- 底部按钮区域 ---
        button_layout = QHBoxLayout()
        self.btn_start_compile = QPushButton("开始编译")
        self.btn_start_compile.clicked.connect(self.start_compile)
        self.btn_gen_command = QPushButton("生成构建命令")
        self.btn_gen_command.clicked.connect(lambda: self.get_command(dry_run=True))
        button_layout.addStretch()
        button_layout.addWidget(self.btn_gen_command)
        button_layout.addWidget(self.btn_start_compile)

        # --- 状态栏 ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

        # 将所有部分添加到主布局
        main_layout.addWidget(basic_info_group)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(console_splitter)
        main_layout.addLayout(button_layout)

        # --- 连接 Worker 信号 ---
        self.worker.output_received.connect(self.append_to_console)
        self.worker.error_received.connect(self.append_error_to_console)
        self.worker.finished.connect(self.on_compile_finished)

    def setup_basic_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        mode_group = QGroupBox("编译模式")
        mode_layout = QVBoxLayout(mode_group)
        self.mode_var = "accelerated" # Default
        modes = [
            ("依赖Python解释器模式", "accelerated"),
            ("独立文件夹模式", "standalone"),
            ("单文件模式", "onefile"),
            ("APP模式", "app"), # Note: This might not be a standard Nuitka mode
            ("二进制动态模块模式", "module"),
            ("二进制动态包模式", "package"),
            ("动态链接库模式", "dll")
        ]
        self.mode_buttons = {}
        for text, value in modes:
            rb = QRadioButton(text)
            rb.setChecked(value == self.mode_var)
            rb.toggled.connect(lambda checked, v=value: self.on_mode_changed(v) if checked else None)
            self.mode_buttons[value] = rb
            mode_layout.addWidget(rb)

        flags_group = QGroupBox("Python 标志")
        flags_layout = QVBoxLayout(flags_group)
        self.flag_vars = {
            'isolated': False,
            'main': False,
            'no_asserts': False,
            'no_docstrings': False,
            'no_site': False,
            'no_warnings': False,
            'safe_path': False,
            'static_hashes': False,
            'unbuffered': False,
            'dont_write_bytecode': False,
        }
        for flag in self.flag_vars.keys():
            cb = QCheckBox(flag.replace('_', '-'))
            setattr(self, f'var_{flag}', cb.isChecked) # Store getter function
            setattr(self, f'cbtn_{flag}', cb) # Store widget
            flags_layout.addWidget(cb)

        debug_group = QGroupBox("调试选项")
        debug_layout = QVBoxLayout(debug_group)
        self.py_dbg_var = False
        self.py_dbg_checkbox = QCheckBox("Python Debug")
        self.py_dbg_checkbox.stateChanged.connect(lambda s: setattr(self, 'py_dbg_var', s == Qt.Checked))
        debug_layout.addWidget(self.py_dbg_checkbox)

        self.c_pgo_var = False
        self.c_pgo_checkbox = QCheckBox("C层级的PGO优化(独立模式不可用)")
        self.c_pgo_checkbox.stateChanged.connect(lambda s: setattr(self, 'c_pgo_var', s == Qt.Checked))
        debug_layout.addWidget(self.c_pgo_checkbox)

        # Add groups to tab layout
        top_bottom_splitter = QSplitter(Qt.Horizontal)
        left_side = QWidget()
        left_layout = QVBoxLayout(left_side)
        left_layout.addWidget(mode_group)
        left_layout.addWidget(debug_group)
        right_side = QWidget()
        right_layout = QVBoxLayout(right_side)
        right_layout.addWidget(flags_group)

        top_bottom_splitter.addWidget(left_side)
        top_bottom_splitter.addWidget(right_side)
        layout.addWidget(top_bottom_splitter)
        self.tabs.addTab(tab, "基本选项")

    def setup_package_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.prefer_source_code_var = False
        self.prefer_source_code_checkbox = QCheckBox("优先使用源代码而不是已经编译的扩展模块")
        self.prefer_source_code_checkbox.stateChanged.connect(lambda s: setattr(self, 'prefer_source_code_var', s == Qt.Checked))
        layout.addWidget(self.prefer_source_code_checkbox)

        # Use a splitter for the four include sections
        include_splitter = QSplitter(Qt.Horizontal)
        include_splitter.setChildrenCollapsible(False)

        # Define a helper function to create a section
        def create_include_section(title, var_attr, list_attr, add_cmd):
            group = QGroupBox(title)
            group_layout = QVBoxLayout(group)

            input_hbox = QHBoxLayout()
            entry = QLineEdit()
            setattr(self, var_attr, entry.text) # Store getter
            btn_add = QPushButton("添加")
            btn_del = QPushButton("删除选中")
            input_hbox.addWidget(entry)
            input_hbox.addWidget(btn_add)
            input_hbox.addWidget(btn_del)
            group_layout.addLayout(input_hbox)

            list_widget = QListWidget()
            setattr(self, list_attr, list_widget) # Store widget
            group_layout.addWidget(list_widget)

            btn_add.clicked.connect(lambda: self.insert_item(list_widget, entry, add_cmd))
            btn_del.clicked.connect(lambda: self.delete_selected_item(list_widget, add_cmd))

            return group

        include_package_group = create_include_section(
            "包含整个包", "include_package_var", "include_package_list",
            lambda: self.includes_content.setdefault('include_package', []).append(self.include_package_var())
        )
        include_module_group = create_include_section(
            "包含单个模块", "include_module_var", "include_module_list",
            lambda: self.includes_content.setdefault('include_module', []).append(self.include_module_var())
        )
        include_plugin_dir_group = create_include_section(
            "包含插件目录", "include_plugin_directory_var", "include_plugin_directory_list",
            lambda: self.includes_content.setdefault('include_plugin_directory', []).append(self.include_plugin_directory_var())
        )
        include_plugin_files_group = create_include_section(
            "包含插件文件", "include_plugin_files_var", "include_plugin_files_list",
            lambda: self.includes_content.setdefault('include_plugin_files', []).append(self.include_plugin_files_var())
        )

        include_splitter.addWidget(include_package_group)
        include_splitter.addWidget(include_module_group)
        include_splitter.addWidget(include_plugin_dir_group)
        include_splitter.addWidget(include_plugin_files_group)

        layout.addWidget(include_splitter)
        self.includes_content = {
            'include_package': [],
            'include_module': [],
            'include_plugin_directory': [],
            'include_plugin_files': []
        }
        self.tabs.addTab(tab, "包含包选项")

    def setup_imports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Follow imports section
        follow_group = QGroupBox("包含包")
        follow_layout = QFormLayout(follow_group)

        self.follow_imports_var = True
        self.follow_stdlib_var = True
        cbtn_follow = QCheckBox("递归处理导入模块(推荐)")
        cbtn_follow.setChecked(self.follow_imports_var)
        cbtn_follow.stateChanged.connect(lambda s: setattr(self, 'follow_imports_var', s == Qt.Checked))

        cbtn_stdlib = QCheckBox("递归处理标准库导入(推荐)")
        cbtn_stdlib.setChecked(self.follow_stdlib_var)
        cbtn_stdlib.stateChanged.connect(lambda s: setattr(self, 'follow_stdlib_var', s == Qt.Checked))

        pkg_input = QLineEdit()
        btn_add_pkg = QPushButton("添加库")
        btn_del_pkg = QPushButton("删除选中库")

        pkg_list = QListWidget()
        self.follow_imports_list = []
        btn_add_pkg.clicked.connect(lambda: self.insert_item(pkg_list, pkg_input, lambda: self.follow_imports_list.append(pkg_input.text()) or pkg_input.clear()))
        btn_del_pkg.clicked.connect(lambda: self.delete_selected_item(pkg_list, lambda: self.follow_imports_list.pop(pkg_list.currentRow()) if pkg_list.currentRow() >= 0 else None))

        follow_layout.addRow(cbtn_follow)
        follow_layout.addRow(cbtn_stdlib)
        follow_layout.addRow("递归处理导入库:", pkg_input)
        follow_layout.addRow(btn_add_pkg, btn_del_pkg)
        follow_layout.addRow("包含库列表:", pkg_list)

        # No follow imports section
        no_follow_group = QGroupBox("不包含库")
        no_follow_layout = QFormLayout(no_follow_group)

        self.no_follow_imports_var = False
        cbtn_no_follow = QCheckBox("不递归处理一切导入库(覆盖所有包含选项)(不推荐)")
        cbtn_no_follow.stateChanged.connect(lambda s: setattr(self, 'no_follow_imports_var', s == Qt.Checked))

        pkg_input_2 = QLineEdit()
        btn_add_pkg_2 = QPushButton("添加库")
        btn_del_pkg_2 = QPushButton("删除选中库")

        pkg_list_2 = QListWidget()
        self.no_follow_imports_list = []
        btn_add_pkg_2.clicked.connect(lambda: self.insert_item(pkg_list_2, pkg_input_2, lambda: self.no_follow_imports_list.append(pkg_input_2.text()) or pkg_input_2.clear()))
        btn_del_pkg_2.clicked.connect(lambda: self.delete_selected_item(pkg_list_2, lambda: self.no_follow_imports_list.pop(pkg_list_2.currentRow()) if pkg_list_2.currentRow() >= 0 else None))

        no_follow_layout.addRow(cbtn_no_follow)
        no_follow_layout.addRow("不递归处理导入库:", pkg_input_2)
        no_follow_layout.addRow(btn_add_pkg_2, btn_del_pkg_2)
        no_follow_layout.addRow("不包含库列表:", pkg_list_2)

        # Add groups to tab
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(follow_group)
        splitter.addWidget(no_follow_group)
        layout.addWidget(splitter)
        self.tabs.addTab(tab, "导入选项")

    def setup_onefile_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.onefile_no_compression_var = False
        self.onefile_no_compression_checkbox = QCheckBox("不压缩单文件包")
        self.onefile_no_compression_checkbox.stateChanged.connect(lambda s: setattr(self, 'onefile_no_compression_var', s == Qt.Checked))
        layout.addWidget(self.onefile_no_compression_checkbox)

        self.onefile_as_archive_var = False
        self.onefile_as_archive_checkbox = QCheckBox("创建可以使用nuitka-onefile-unapck解包的归档格式")
        self.onefile_as_archive_checkbox.stateChanged.connect(lambda s: setattr(self, 'onefile_as_archive_var', s == Qt.Checked))
        layout.addWidget(self.onefile_as_archive_checkbox)

        self.onefile_no_dll_var = False
        self.onefile_no_dll_checkbox = QCheckBox("不使用DLL文件在运行之前解压, 使用EXE解压")
        self.onefile_no_dll_checkbox.stateChanged.connect(lambda s: setattr(self, 'onefile_no_dll_var', s == Qt.Checked))
        layout.addWidget(self.onefile_no_dll_checkbox)

        form_layout = QFormLayout()
        self.onefile_tempdir_spec_var = ""
        self.onefile_tempdir_spec_edit = QLineEdit()
        self.onefile_tempdir_spec_edit.textChanged.connect(lambda t: setattr(self, 'onefile_tempdir_spec_var', t))
        form_layout.addRow("单文件临时目录:", self.onefile_tempdir_spec_edit)

        self.onefile_cache_mode_var = "auto"
        self.onefile_cache_mode_combo = QComboBox()
        self.onefile_cache_mode_combo.addItems(["auto", "tempdir", "userdir"])
        self.onefile_cache_mode_combo.setCurrentText(self.onefile_cache_mode_var)
        self.onefile_cache_mode_combo.currentTextChanged.connect(lambda t: setattr(self, 'onefile_cache_mode_var', t))
        form_layout.addRow("单文件缓存模式:", self.onefile_cache_mode_combo)

        self.onefile_child_grace_var = 5000
        self.onefile_child_grace_spinbox = QSpinBox()
        self.onefile_child_grace_spinbox.setRange(0, 30000)
        self.onefile_child_grace_spinbox.setSingleStep(500)
        self.onefile_child_grace_spinbox.setValue(self.onefile_child_grace_var)
        self.onefile_child_grace_spinbox.valueChanged.connect(lambda v: setattr(self, 'onefile_child_grace_var', v))
        form_layout.addRow("单文件子进程终止等待时间(毫秒):", self.onefile_child_grace_spinbox)

        layout.addLayout(form_layout)
        self.tabs.addTab(tab, "单文件选项")

    def setup_data_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Create a scroll area for the potentially large number of data options
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Helper to create a section with source and destination inputs
        def create_data_section(title, src_var_attr, dst_var_attr, list_src_attr, list_dst_attr, data_dict_attr, add_callback, del_callback):
            group = QGroupBox(title)
            group_layout = QFormLayout(group)

            src_input = QLineEdit()
            dst_input = QLineEdit()
            btn_browse = QPushButton("浏览")
            btn_insert = QPushButton("插入")
            btn_delete = QPushButton("删除选中")

            # List widgets for source and destination
            src_list = QListWidget()
            dst_list = QListWidget()

            # Set up connections
            setattr(self, src_var_attr, src_input.text)
            setattr(self, dst_var_attr, dst_input.text)
            setattr(self, list_src_attr, src_list)
            setattr(self, list_dst_attr, dst_list)
            setattr(self, data_dict_attr, {})
            
            btn_browse.clicked.connect(lambda: self.select_data_file(src_input))
            btn_insert.clicked.connect(lambda: self.insert_cascade_item(src_list, dst_list, getattr(self, data_dict_attr), src_input, dst_input, add_callback))
            btn_delete.clicked.connect(lambda: self.delete_cascade_selection(src_list, dst_list, getattr(self, data_dict_attr), del_callback))

            # Layout
            input_hbox = QHBoxLayout()
            input_hbox.addWidget(QLabel("包含数据文件:"))
            input_hbox.addWidget(src_input)
            input_hbox.addWidget(QLabel("到:"))
            input_hbox.addWidget(dst_input)
            input_hbox.addWidget(btn_browse)
            input_hbox.addWidget(btn_insert)
            input_hbox.addWidget(btn_delete)

            list_hbox = QHBoxLayout()
            list_hbox.addWidget(src_list)
            list_hbox.addWidget(dst_list)

            group_layout.addRow(input_hbox)
            group_layout.addRow(list_hbox)

            return group

        # Include package data files
        pkg_data_group = QGroupBox("包含包数据文件")
        pkg_data_layout = QHBoxLayout(pkg_data_group)
        pkg_data_input = QLineEdit()
        pkg_data_btn_add = QPushButton("添加")
        pkg_data_btn_del = QPushButton("删除选中")
        pkg_data_list = QListWidget()
        self.include_package_data_list = pkg_data_list
        self.include_package_data = []
        pkg_data_btn_add.clicked.connect(lambda: self.insert_item(pkg_data_list, pkg_data_input, lambda: self.include_package_data.append(pkg_data_input.text()) or pkg_data_input.clear()))
        pkg_data_btn_del.clicked.connect(lambda: self.delete_selected_item(pkg_data_list, lambda: self.include_package_data.pop(pkg_data_list.currentRow()) if pkg_data_list.currentRow() >= 0 else None))
        pkg_data_layout.addWidget(QLabel("包含包数据文件的包"))
        pkg_data_layout.addWidget(pkg_data_input)
        pkg_data_layout.addWidget(pkg_data_btn_add)
        pkg_data_layout.addWidget(pkg_data_btn_del)
        pkg_data_layout.addWidget(pkg_data_list)
        scroll_layout.addWidget(pkg_data_group)

        # No include data files patterns
        no_data_group = QGroupBox("不包含的数据文件模式")
        no_data_layout = QHBoxLayout(no_data_group)
        no_data_input = QLineEdit()
        no_data_btn_add = QPushButton("添加")
        no_data_btn_del = QPushButton("删除选中")
        no_data_list = QListWidget()
        self.noinclude_data_files_list = no_data_list
        self.noinclude_data_files = []
        no_data_btn_add.clicked.connect(lambda: self.insert_item(no_data_list, no_data_input, lambda: self.noinclude_data_files.append(no_data_input.text()) or no_data_input.clear()))
        no_data_btn_del.clicked.connect(lambda: self.delete_selected_item(no_data_list, lambda: self.noinclude_data_files.pop(no_data_list.currentRow()) if no_data_list.currentRow() >= 0 else None))
        no_data_layout.addWidget(QLabel("不包含的数据文件模式"))
        no_data_layout.addWidget(no_data_input)
        no_data_layout.addWidget(no_data_btn_add)
        no_data_layout.addWidget(no_data_btn_del)
        no_data_layout.addWidget(no_data_list)
        scroll_layout.addWidget(no_data_group)

        # Include data files
        data_files_group = create_data_section(
            "包含的数据文件",
            "include_data_files_src_var", "include_data_files_dst_var",
            "include_data_files_src_list", "include_data_files_dst_list",
            "include_data_files_dict",
            lambda k, v: self.include_data_files_dict.update({k: v}),
            lambda k: self.include_data_files_dict.pop(k, None)
        )
        scroll_layout.addWidget(data_files_group)

        # Include onefile external data
        onefile_ext_group = create_data_section(
            "包含的单文件外部数据文件",
            "include_onefile_external_data_src_var", "include_onefile_external_data_dst_var",
            "include_onefile_external_data_src_list", "include_onefile_external_data_dst_list",
            "include_onefile_external_data_dict",
            lambda k, v: self.include_onefile_external_data_dict.update({k: v}),
            lambda k: self.include_onefile_external_data_dict.pop(k, None)
        )
        scroll_layout.addWidget(onefile_ext_group)

        # Include data dir
        data_dir_group = create_data_section(
            "包含的目录",
            "include_data_dir_src_var", "include_data_dir_dst_var",
            "include_data_dir_src_list", "include_data_dir_dst_list",
            "include_data_dir_dict",
            lambda k, v: self.include_data_dir_dict.update({k: v}),
            lambda k: self.include_data_dir_dict.pop(k, None)
        )
        scroll_layout.addWidget(data_dir_group)

        # Include raw dir
        raw_dir_group = create_data_section(
            "包含的原始目录(权限不变)",
            "include_raw_dir_src_var", "include_raw_dir_dst_var",
            "include_raw_dir_src_list", "include_raw_dir_dst_list",
            "include_raw_dir_dict",
            lambda k, v: self.include_raw_dir_dict.update({k: v}),
            lambda k: self.include_raw_dir_dict.pop(k, None)
        )
        scroll_layout.addWidget(raw_dir_group)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        self.tabs.addTab(tab, "数据文件")

    def setup_dll_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.noinclude_dlls_var = ""
        self.noinclude_dlls_edit = QLineEdit()
        self.noinclude_dlls_edit.textChanged.connect(lambda t: setattr(self, 'noinclude_dlls_var', t))
        layout.addRow("不包含DLL列表:", self.noinclude_dlls_edit)

        self.list_package_dlls_var = ""
        self.list_package_dlls_edit = QLineEdit()
        self.list_package_dlls_edit.textChanged.connect(lambda t: setattr(self, 'list_package_dlls_var', t))
        layout.addRow("列出包所包含的DLL:", self.list_package_dlls_edit)

        self.list_package_exe_var = ""
        self.list_package_exe_edit = QLineEdit()
        self.list_package_exe_edit.textChanged.connect(lambda t: setattr(self, 'list_package_exe_var', t))
        layout.addRow("列出包所包含的EXE:", self.list_package_exe_edit)

        self.tabs.addTab(tab, "DLL选项")

    def setup_warn_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.warn_implicit_exception_var = False
        self.warn_implicit_exception_checkbox = QCheckBox("启用编译时隐式异常警告")
        self.warn_implicit_exception_checkbox.stateChanged.connect(lambda s: setattr(self, 'warn_implicit_exception_var', s == Qt.Checked))
        layout.addWidget(self.warn_implicit_exception_checkbox)

        self.warn_unusual_code_var = False
        self.warn_unusual_code_checkbox = QCheckBox("启用编译时检测到的异常代码警告")
        self.warn_unusual_code_checkbox.stateChanged.connect(lambda s: setattr(self, 'warn_unusual_code_var', s == Qt.Checked))
        layout.addWidget(self.warn_unusual_code_checkbox)

        self.assume_yes_for_downloads_var = True
        self.assume_yes_for_downloads_checkbox = QCheckBox("允许Nuitka在必要时下载外部代码(主要是编译器及其依赖)(⚠警告:不要轻易禁用)")
        self.assume_yes_for_downloads_checkbox.setChecked(self.assume_yes_for_downloads_var)
        self.assume_yes_for_downloads_checkbox.stateChanged.connect(lambda s: setattr(self, 'assume_yes_for_downloads_var', s == Qt.Checked))
        layout.addWidget(self.assume_yes_for_downloads_checkbox)

        warn_form_layout = QFormLayout()
        self.nowarn_mnemonic_var = ""
        self.nowarn_mnemonic_edit = QLineEdit()
        self.nowarn_mnemonic_edit.textChanged.connect(lambda t: setattr(self, 'nowarn_mnemonic_var', t))
        warn_form_layout.addRow("禁用特定助记符的警告:", self.nowarn_mnemonic_edit)

        layout.addLayout(warn_form_layout)
        self.tabs.addTab(tab, "警告控制")

    def setup_run_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.run_var = False
        self.run_checkbox = QCheckBox("编译后立即执行")
        self.run_checkbox.stateChanged.connect(lambda s: setattr(self, 'run_var', s == Qt.Checked))
        layout.addWidget(self.run_checkbox)

        self.debugger_var = False
        self.debugger_checkbox = QCheckBox("调试器中运行(自动选择gdb/lldb)")
        self.debugger_checkbox.stateChanged.connect(lambda s: setattr(self, 'debugger_var', s == Qt.Checked))
        layout.addWidget(self.debugger_checkbox)

        self.tabs.addTab(tab, "运行选项")

    def setup_compile_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.full_compat_var = False
        self.full_compat_checkbox = QCheckBox("启用完全兼容CPython模式(测试)")
        self.full_compat_checkbox.stateChanged.connect(lambda s: setattr(self, 'full_compat_var', s == Qt.Checked))
        layout.addRow(self.full_compat_checkbox)

        self.file_reference_choice_var = ""
        self.file_reference_combo = QComboBox()
        self.file_reference_combo.addItems(["runtime", "original", "frozen"])
        self.file_reference_combo.currentTextChanged.connect(lambda t: setattr(self, 'file_reference_choice_var', t))
        layout.addRow("选择__file__变量的值:", self.file_reference_combo)

        self.module_name_choice_var = ""
        self.module_name_combo = QComboBox()
        self.module_name_combo.addItems(["runtime", "original"])
        self.module_name_combo.currentTextChanged.connect(lambda t: setattr(self, 'module_name_choice_var', t))
        layout.addRow("选择__name__变量和__package__变量的值:", self.module_name_combo)

        self.user_package_configuration_var = ""
        self.user_package_configuration_edit = QLineEdit()
        self.user_package_configuration_edit.setReadOnly(True)
        btn_browse_yaml = QPushButton("浏览")
        btn_browse_yaml.clicked.connect(self.select_yaml_file)
        yaml_hbox = QHBoxLayout()
        yaml_hbox.addWidget(self.user_package_configuration_edit)
        yaml_hbox.addWidget(btn_browse_yaml)
        layout.addRow("用户包配置YAML文件路径:", yaml_hbox)

        self.tabs.addTab(tab, "编译选项")

    def setup_output_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.remove_output_var = True
        self.remove_output_checkbox = QCheckBox("编译完成后删除中间文件")
        self.remove_output_checkbox.setChecked(self.remove_output_var)
        self.remove_output_checkbox.stateChanged.connect(lambda s: setattr(self, 'remove_output_var', s == Qt.Checked))
        layout.addRow(self.remove_output_checkbox)

        self.no_pyi_file_var = False
        self.no_pyi_file_checkbox = QCheckBox("不为扩展模块创建pyi文件")
        self.no_pyi_file_checkbox.stateChanged.connect(lambda s: setattr(self, 'no_pyi_file_var', s == Qt.Checked))
        layout.addRow(self.no_pyi_file_checkbox)

        self.output_filename_var = ""
        self.output_filename_edit = QLineEdit()
        self.output_filename_edit.textChanged.connect(lambda t: setattr(self, 'output_filename_var', t))
        layout.addRow("可执行文件名:", self.output_filename_edit)

        self.output_dir_var = ""
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        btn_browse_dir = QPushButton("浏览")
        btn_browse_dir.clicked.connect(self.select_save_dir)
        dir_hbox = QHBoxLayout()
        dir_hbox.addWidget(self.output_dir_edit)
        dir_hbox.addWidget(btn_browse_dir)
        layout.addRow("输出文件目录:", dir_hbox)

        self.tabs.addTab(tab, "输出控制")

    def setup_deployment_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.deployment_var = 1 # Default
        deploy_group = QGroupBox("部署选项")
        deploy_layout = QVBoxLayout(deploy_group)

        rbtn_deploy_disabled = QRadioButton("禁用使查找兼容性问题更容易的代码")
        rbtn_deploy_partial = QRadioButton("保持部署模式但禁用部分功能")
        rbtn_deploy_none = QRadioButton("不进行处理")
        rbtn_deploy_none.setChecked(True) # Default

        self.no_deployment_flag_edit = QLineEdit()
        self.no_deployment_flag_edit.setEnabled(False) # Initially disabled

        def on_radio_toggled():
            if rbtn_deploy_partial.isChecked():
                self.no_deployment_flag_edit.setEnabled(True)
                self.deployment_var = 1
            elif rbtn_deploy_disabled.isChecked():
                self.no_deployment_flag_edit.setEnabled(False)
                self.deployment_var = 2
            else: # rbtn_deploy_none
                self.no_deployment_flag_edit.setEnabled(False)
                self.deployment_var = 0

        rbtn_deploy_disabled.toggled.connect(on_radio_toggled)
        rbtn_deploy_partial.toggled.connect(on_radio_toggled)
        rbtn_deploy_none.toggled.connect(on_radio_toggled)

        deploy_layout.addWidget(rbtn_deploy_disabled)
        deploy_layout.addWidget(rbtn_deploy_partial)
        deploy_layout.addWidget(QLabel("禁用选项"))
        deploy_layout.addWidget(self.no_deployment_flag_edit)
        deploy_layout.addWidget(rbtn_deploy_none)

        layout.addWidget(deploy_group)
        self.tabs.addTab(tab, "部署选项")

    def setup_debug_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        debug_opts_group = QGroupBox("调试性选项(不建议)")
        debug_opts_layout = QVBoxLayout(debug_opts_group)

        self.debug_var = False
        self.debug_checkbox = QCheckBox("执行所有可能的自检以查错")
        self.debug_checkbox.stateChanged.connect(lambda s: setattr(self, 'debug_var', s == Qt.Checked))
        debug_opts_layout.addWidget(self.debug_checkbox)

        self.unstripped_var = False
        self.unstripped_checkbox = QCheckBox("在结果对象文件中保留调试信息")
        self.unstripped_checkbox.stateChanged.connect(lambda s: setattr(self, 'unstripped_var', s == Qt.Checked))
        debug_opts_layout.addWidget(self.unstripped_checkbox)

        self.trace_execution_var = False
        self.trace_execution_checkbox = QCheckBox("跟踪执行输出(执行前输出代码行)")
        self.trace_execution_checkbox.stateChanged.connect(lambda s: setattr(self, 'trace_execution_var', s == Qt.Checked))
        debug_opts_layout.addWidget(self.trace_execution_checkbox)

        debug_opt_group = QGroupBox("调试与优化")
        debug_opt_layout = QFormLayout(debug_opt_group)

        self.xml_filename_var = ""
        self.xml_filename_edit = QLineEdit()
        self.xml_filename_edit.setReadOnly(True)
        btn_browse_xml = QPushButton("浏览")
        btn_browse_xml.clicked.connect(self.select_xml)
        xml_hbox = QHBoxLayout()
        xml_hbox.addWidget(self.xml_filename_edit)
        xml_hbox.addWidget(btn_browse_xml)
        debug_opt_layout.addRow("将优化结果与程序结构写入的XML文件:", xml_hbox)

        self.low_memory_var = False
        self.low_memory_checkbox = QCheckBox("降低内存用量")
        self.low_memory_checkbox.stateChanged.connect(lambda s: setattr(self, 'low_memory_var', s == Qt.Checked))
        debug_opt_layout.addRow(self.low_memory_checkbox)

        layout.addWidget(debug_opts_group)
        layout.addWidget(debug_opt_group)
        self.tabs.addTab(tab, "调试选项")

    def setup_c_compiler_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        compiler_group = QGroupBox("C 编译器")
        compiler_layout = QVBoxLayout(compiler_group)

        self.C_complier_var = "mingw64" # Default
        rbtn_mingw = QRadioButton("MinGW64编译器")
        rbtn_clang = QRadioButton("Clang编译器")
        rbtn_zig = QRadioButton("Zig编译器")
        rbtn_msvc = QRadioButton("MSVC编译器(下面填写版本)")

        rbtn_mingw.setChecked(True) # Default
        rbtn_mingw.toggled.connect(lambda checked: setattr(self, 'C_complier_var', 'mingw64') if checked else None)
        rbtn_clang.toggled.connect(lambda checked: setattr(self, 'C_complier_var', 'clang') if checked else None)
        rbtn_zig.toggled.connect(lambda checked: setattr(self, 'C_complier_var', 'zig') if checked else None)
        rbtn_msvc.toggled.connect(lambda checked: setattr(self, 'C_complier_var', 'msvc') if checked else None)

        compiler_layout.addWidget(rbtn_mingw)
        compiler_layout.addWidget(rbtn_clang)
        compiler_layout.addWidget(rbtn_zig)
        compiler_layout.addWidget(rbtn_msvc)

        msvc_version_layout = QHBoxLayout()
        msvc_version_layout.addWidget(QLabel("MSVC 版本:"))
        self.msvc_version_combo = QComboBox()
        self.msvc_version_combo.addItems(["latest"]) # Add more versions as needed
        self.msvc_version_combo.setCurrentText("latest")
        self.msvc_version_combo.currentTextChanged.connect(lambda t: setattr(self, 'msvc_version_var', t))
        self.msvc_version_var = "latest"
        msvc_version_layout.addWidget(self.msvc_version_combo)
        compiler_layout.addLayout(msvc_version_layout)

        accel_group = QGroupBox("加速与优化")
        accel_layout = QFormLayout(accel_group)

        self.jobs_var = "auto"
        self.jobs_combo = QComboBox()
        self.jobs_combo.addItems(["auto", "1", "2", "4", "8", "16"])
        self.jobs_combo.setCurrentText(self.jobs_var)
        self.jobs_combo.currentTextChanged.connect(lambda t: setattr(self, 'jobs_var', t))
        accel_layout.addRow("并行编译作业数:", self.jobs_combo)

        self.lto_var = "yes"
        self.lto_combo = QComboBox()
        self.lto_combo.addItems(["yes", "no", "auto"])
        self.lto_combo.setCurrentText(self.lto_var)
        self.lto_combo.currentTextChanged.connect(lambda t: setattr(self, 'lto_var', t))
        accel_layout.addRow("链接时优化(LTO):", self.lto_combo)

        self.static_libpython_var = "auto"
        self.static_libpython_combo = QComboBox()
        self.static_libpython_combo.addItems(["auto", "yes", "no"])
        self.static_libpython_combo.setCurrentText(self.static_libpython_var)
        self.static_libpython_combo.currentTextChanged.connect(lambda t: setattr(self, 'static_libpython_var', t))
        accel_layout.addRow("静态链接Python库:", self.static_libpython_combo)

        self.cf_protection_var = "auto"
        self.cf_protection_combo = QComboBox()
        self.cf_protection_combo.addItems(["auto", "none"])
        self.cf_protection_combo.setCurrentText(self.cf_protection_var)
        self.cf_protection_combo.currentTextChanged.connect(lambda t: setattr(self, 'cf_protection_var', t))
        accel_layout.addRow("GCC的cf-protection模式:", self.cf_protection_combo)

        layout.addWidget(compiler_group)
        layout.addWidget(accel_group)
        self.tabs.addTab(tab, "C 编译器")

    def setup_os_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        win_group = QGroupBox("Windows 选项")
        win_layout = QVBoxLayout(win_group)

        self.windows_uac_admin_var = False
        self.windows_uac_admin_checkbox = QCheckBox("向Windows用户账户控制请求管理员权限")
        self.windows_uac_admin_checkbox.stateChanged.connect(lambda s: setattr(self, 'windows_uac_admin_var', s == Qt.Checked))
        win_layout.addWidget(self.windows_uac_admin_checkbox)

        self.windows_uac_uiaccess_var = False
        self.windows_uac_uiaccess_checkbox = QCheckBox("请求Windows用户账户控制UI访问权限")
        self.windows_uac_uiaccess_checkbox.stateChanged.connect(lambda s: setattr(self, 'windows_uac_uiaccess_var', s == Qt.Checked))
        win_layout.addWidget(self.windows_uac_uiaccess_checkbox)

        console_mode_group = QGroupBox("控制台模式")
        console_mode_layout = QVBoxLayout(console_mode_group)
        self.windows_console_mode_var = "force" # Default
        console_modes = {
            "force": "执行时跳出控制台",
            "disable": "禁用控制台",
            "attach": "从命令行启动时控制台附加到原控制台, 双击启动无控制台",
            "hide": "控制台会被创建, 但会被最小化, 中途可能突然跳出"
        }
        self.console_mode_buttons = {}
        for key, desc in console_modes.items():
            rb = QRadioButton(desc)
            rb.setChecked(key == self.windows_console_mode_var)
            rb.toggled.connect(lambda checked, k=key: setattr(self, 'windows_console_mode_var', k) if checked else None)
            self.console_mode_buttons[key] = rb
            console_mode_layout.addWidget(rb)

        icon_group = QGroupBox("Windows 应用程序 ICO 图标")
        icon_layout = QVBoxLayout(icon_group)

        icon_input_hbox = QHBoxLayout()
        self.win_ico_path_edit = QLineEdit()
        self.win_ico_path_edit.setReadOnly(True)
        btn_browse_ico = QPushButton("浏览")
        btn_browse_ico.clicked.connect(self.select_ico)
        icon_input_hbox.addWidget(self.win_ico_path_edit)
        icon_input_hbox.addWidget(btn_browse_ico)
        icon_layout.addLayout(icon_input_hbox)

        icon_list_hbox = QHBoxLayout()
        self.win_ico_list = QListWidget()
        btn_add_ico = QPushButton("插入")
        btn_del_ico = QPushButton("删除选中")
        btn_add_ico.clicked.connect(lambda: self.insert_item(self.win_ico_list, self.win_ico_path_edit, lambda: self.windows_icon_from_ico.append(self.win_ico_path_edit.text()) or self.win_ico_path_edit.clear()))
        btn_del_ico.clicked.connect(lambda: self.delete_selected_item(self.win_ico_list, lambda: self.windows_icon_from_ico.pop(self.win_ico_list.currentRow()) if self.win_ico_list.currentRow() >= 0 else None))
        icon_list_hbox.addWidget(self.win_ico_list)
        ico_btn_vbox = QVBoxLayout()
        ico_btn_vbox.addWidget(btn_add_ico)
        ico_btn_vbox.addWidget(btn_del_ico)
        ico_btn_vbox.addStretch()
        icon_list_hbox.addLayout(ico_btn_vbox)
        icon_layout.addLayout(icon_list_hbox)
        self.windows_icon_from_ico = []

        win_splitter = QSplitter(Qt.Horizontal)
        win_left = QWidget()
        win_left_layout = QVBoxLayout(win_left)
        win_left_layout.addWidget(console_mode_group)
        win_right = QWidget()
        win_right_layout = QVBoxLayout(win_right)
        win_right_layout.addWidget(icon_group)
        win_splitter.addWidget(win_left)
        win_splitter.addWidget(win_right)
        win_layout.addWidget(win_splitter)

        linux_group = QGroupBox("Linux 选项")
        linux_layout = QHBoxLayout(linux_group)
        self.linux_icon_edit = QLineEdit()
        self.linux_icon_edit.setReadOnly(True)
        btn_browse_linux_ico = QPushButton("浏览")
        btn_browse_linux_ico.clicked.connect(self.select_ico)
        linux_layout.addWidget(QLabel("Linux 单文件图标:"))
        linux_layout.addWidget(self.linux_icon_edit)
        linux_layout.addWidget(btn_browse_linux_ico)

        layout.addWidget(win_group)
        layout.addWidget(linux_group)
        self.tabs.addTab(tab, "系统选项")

    def setup_info_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.company_name_var = ""
        self.product_name_var = ""
        self.file_version_var = ""
        self.product_version_var = ""
        self.copyright_text_var = "Copyright @2026"
        self.trademarks_var = ""

        fields = [
            ("版本信息中公司名称", "company_name_var"),
            ("版本信息中产品名称", "product_name_var"),
            ("版本信息中文件版本", "file_version_var"),
            ("版本信息中产品版本", "product_version_var"),
            ("版本信息中版权信息", "copyright_text_var"),
            ("版本信息中商标", "trademarks_var"),
        ]

        for label, var_name in fields:
            edit = QLineEdit()
            setattr(self, f"{var_name}_edit", edit) # Store widget reference
            edit.textChanged.connect(lambda t, vn=var_name: setattr(self, vn, t))
            layout.addRow(label, edit)

        self.tabs.addTab(tab, "版本信息")

    def setup_plugin_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        plugins = [
            "anti-bloat", "data-files", "delvewheel", "dill-compat", "dll-files",
            "enum-compat", "eventlet", "gevent", "gi", "glfw", "implicit-imports",
            "kivy", "matplotlib", "multiprocessing", "no-qt", "options-nanny",
            "pbr-compat", "pkg-resources", "playwright", "pmw-freezer", "pylint-warnings",
            "pyqt5", "pyqt6", "pyside2", "pyside6", "pywebview", "spacy", "tk-inter", "transformers"
        ]
        self.plugin_vars = {}
        plugin_group = QGroupBox("启用插件")
        plugin_grid_layout = QGridLayout(plugin_group)
        row, col = 0, 0
        max_cols = 6
        for plugin in plugins:
            var_name = f"{plugin.replace('-', '_')}_var"
            checkbox = QCheckBox(plugin)
            setattr(self, var_name, False)
            setattr(self, f"cbtn_{var_name}", checkbox) # Store widget reference
            checkbox.stateChanged.connect(lambda s, vn=var_name: setattr(self, vn, s == Qt.Checked))
            plugin_grid_layout.addWidget(checkbox, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        user_plugin_group = QGroupBox("用户插件")
        user_plugin_layout = QHBoxLayout(user_plugin_group)
        self.user_plugin_edit = QLineEdit()
        btn_browse_user_plugin = QPushButton("浏览")
        btn_browse_user_plugin.clicked.connect(self.browse_user_plugin)
        user_plugin_layout.addWidget(QLabel("用户插件路径"))
        user_plugin_layout.addWidget(self.user_plugin_edit)
        user_plugin_layout.addWidget(btn_browse_user_plugin)

        help_group = QGroupBox("标准插件帮助")
        help_layout = QVBoxLayout(help_group)
        self.plugin_help_text = QTextEdit()
        self.plugin_help_text.setReadOnly(True)
        help_text_content = """=======================================================================
anti-bloat 精简优化：从广泛使用的库模块源代码中移除不必要的导入。
data-files 数据文件：根据包配置文件包含指定的数据文件。
delvewheel delvewheel 支持：在独立模式下支持使用 delvewheel 的包所必需。
dill-compat dill 兼容性：为 'dill' 包和 'cloudpickle' 提供兼容性支持所必需。
dll-files DLL 文件：根据包配置文件包含 DLL 文件。
enum-compat 枚举兼容性：为 Python2 和 'enum' 包提供兼容性支持所必需。
eventlet eventlet 支持：支持包含 'eventlet' 依赖项及其对 'dns' 包进行动态补丁的需求。
gevent gevent 支持：为 'gevent' 包所必需。
gi GI (GObject Introspection) 支持：支持 GI 包的 typelib 依赖。
glfw glfw 支持：在独立模式下为 'OpenGL' (PyOpenGL) 和 'glfw' 包所必需。
implicit-imports 隐式导入：根据包配置文件提供包的隐式导入。
kivy Kivy 支持：为 'kivy' 包所必需。
matplotlib Matplotlib 支持：为 'matplotlib' 模块所必需。
multiprocessing 多进程支持：为 Python 的 'multiprocessing' 模块所必需。
no-qt 禁用 Qt：禁止包含所有 Qt 绑定库。
options-nanny 选项保姆：根据包配置文件，向用户提示潜在问题。
pbr-compat pbr 兼容性：在独立模式下为 'pbr' 包所必需。
pkg-resources pkg_resources 支持：为 'pkg_resources' 提供解决方案。
playwright Playwright 支持：为 'playwright' 包所必需。
pmw-freezer Pmw 支持：为 'Pmw' 包所必需。
pylint-warnings PyLint 警告支持：支持 PyLint / PyDev 的源代码标记。
pyqt5 PyQt5 支持：为 PyQt5 包所必需。
pyqt6 PyQt6 支持：在独立模式下为 PyQt6 包所必需。
pyside2 PySide2 支持：为 PySide2 包所必需。
pyside6 PySide6 支持：在独立模式下为 PySide6 包所必需。
pywebview Webview 支持：为 'webview' 包 (PyPI 上的 pywebview) 所必需。
spacy spaCy 支持：为 'spacy' 包所必需。
tk-inter Tkinter 支持：为 Python 的 Tk 模块所必需。
transformers Transformers支持：为 transformers 包提供隐式导入。
========================================================================"""
        self.plugin_help_text.setPlainText(help_text_content)
        help_layout.addWidget(self.plugin_help_text)

        layout.addWidget(plugin_group)
        layout.addWidget(user_plugin_group)
        layout.addWidget(help_group)
        self.tabs.addTab(tab, "插件选项")

    # --- Helper Methods ---
    def on_mode_changed(self, mode_value):
        self.mode_var = mode_value

    def select_script(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择 Python 脚本", "", "Python 脚本 (*.py *.pyw)")
        if filename:
            self.script_path_edit.setText(filename)

    def select_interpreter(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择 Python 解释器", "", "Python 解释器 (*.exe)" if platform.system() == "Windows" else "Python Interpreter (*)")
        if filename:
            # Basic validation similar to original
            if platform.system() == "Windows":
                pat = r'python(\d{1}\.\d{2})?.exe'
            else:
                pat = r'python(\d{1}\.\d{1,2})'
            if re.search(pat, os.path.basename(filename)):
                self.interpreter_path_edit.setText(filename)
            else:
                QMessageBox.critical(self, "错误", "选择的文件不是 CPython 解释器！")

    def select_ico(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择 ICO 图标", "", "ICO 图标 (*.ico)")
        if filename:
            sender = self.sender()
            # Determine which edit field to update based on the sender
            if sender == self.findChild(type(btn_browse_ico), "btn_browse_ico"): # Not ideal, better to pass target
                 self.win_ico_path_edit.setText(filename)
            else: # Assume it's for linux icon
                 self.linux_icon_edit.setText(filename)

    def select_save_dir(self):
        dirname = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dirname:
            self.output_dir_edit.setText(dirname)

    def select_xml(self):
        filename, _ = QFileDialog.getSaveFileName(self, "选择 XML 输出文件", "", "XML 文件 (*.xml)")
        if filename:
            self.xml_filename_edit.setText(filename)

    def select_yaml_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择 YAML 配置文件", "", "YAML 文件 (*.yml *.yaml)")
        if filename:
            self.user_package_configuration_edit.setText(filename)

    def select_data_file(self, target_edit):
        filename, _ = QFileDialog.getOpenFileName(self, "选择数据文件", "", "所有文件 (*)")
        if filename:
            target_edit.setText(filename.replace('\\', '/'))

    def select_data_dir(self, target_edit):
        dirname = QFileDialog.getExistingDirectory(self, "选择数据目录")
        if dirname:
            target_edit.setText(dirname.replace('\\', '/'))

    def browse_user_plugin(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择用户插件", "", "Python Files (*.py);;All Files (*)")
        if filename:
            self.user_plugin_edit.setText(filename)

    def insert_item(self, list_widget, text_input, add_command):
        text = text_input.text().strip()
        if text:
            list_widget.addItem(text)
            add_command()
            text_input.clear()
        else:
            QMessageBox.warning(self, "警告", "输入不能为空！")

    def delete_selected_item(self, list_widget, del_command):
        current_row = list_widget.currentRow()
        if current_row >= 0:
            list_widget.takeItem(current_row)
            del_command()
        else:
            QMessageBox.warning(self, "警告", "没有选中的项目！")

    def insert_cascade_item(self, src_list, dst_list, data_dict, src_input, dst_input, add_command):
        src_text = src_input.text().strip()
        dst_text = dst_input.text().strip()
        if src_text and dst_text:
            src_list.addItem(src_text)
            dst_list.addItem(dst_text)
            add_command(src_text, dst_text)
            src_input.clear()
            dst_input.clear()
        else:
            QMessageBox.warning(self, "警告", "源和目标路径不能为空！")

    def delete_cascade_selection(self, src_list, dst_list, data_dict, del_command):
        current_row = src_list.currentRow()
        if current_row < 0:
             current_row = dst_list.currentRow()

        if current_row >= 0:
            item_key = src_list.item(current_row).text()
            src_list.takeItem(current_row)
            dst_list.takeItem(current_row)
            del_command(item_key)
        else:
            QMessageBox.warning(self, "警告", "没有选中的项目！")

    def get_command(self, dry_run=True):
        if not self.interpreter_path_edit.text():
            QMessageBox.critical(self, "错误", "请先选择 Python 解释器！")
            return []
        if not self.script_path_edit.text():
            QMessageBox.critical(self, "错误", "请先选择 Python 脚本！")
            return []

        cmd = [
            self.interpreter_path_edit.text(),
            "-m", "nuitka",
            f"--main={self.script_path_edit.text()}",
            f"--mode={self.mode_var}",
            "--verbose",
            "--show-memory"
        ]

        # Add flags
        for flag_name, _ in self.flag_vars.items():
            if getattr(self, f'var_{flag_name}')():
                cmd.append(f"--python-flag={flag_name.replace('_', '-')}")

        if self.py_dbg_var:
            cmd.append("--python-debug")
        if self.c_pgo_var:
            cmd.append("--c-pgo")

        # Add includes
        for pkg in self.includes_content.get('include_package', []):
            cmd.append(f"--include-package={pkg}")
        for mod in self.includes_content.get('include_module', []):
            cmd.append(f"--include-module={mod}")
        for dir_path in self.includes_content.get('include_plugin_directory', []):
            cmd.append(f"--include-plugin-directory={dir_path}")
        for file_path in self.includes_content.get('include_plugin_files', []):
            cmd.append(f"--include-plugin-files={file_path}")

        # Add imports
        if not self.no_follow_imports_var:
            if self.follow_imports_var:
                cmd.append("--follow-imports")
            if self.follow_stdlib_var:
                cmd.append("--follow-stdlib")
            for l in self.follow_imports_list:
                cmd.append(f"--follow-import-to={l}")
            for l in self.no_follow_imports_list:
                cmd.append(f"--nofollow-import-to={l}")
        else:
            cmd.append("--nofollow-imports")

        # Add onefile options
        if self.onefile_as_archive_var:
            cmd.append("--onefile-as-archive")
        if self.onefile_no_compression_var:
            cmd.append("--onefile-no-compression")
        if self.onefile_no_dll_var:
            cmd.append("--onefile-no-dll")
        if self.onefile_child_grace_var != 5000:
            cmd.append(f"--onefile-child-grace={self.onefile_child_grace_var}")
        if self.onefile_cache_mode_var != 'auto':
            cmd.append(f"--onefile-cache-mode={self.onefile_cache_mode_var}")

        # Add data options
        for k, v in self.include_data_dir_dict.items():
            cmd.append(f"--include-data-dir={k}={v}")
        for k, v in self.include_data_files_dict.items():
            cmd.append(f"--include-data-files={k}={v}")
        for k, v in self.include_raw_dir_dict.items():
            cmd.append(f"--include-raw-dir={k}={v}")
        for k, v in self.include_onefile_external_data_dict.items():
            cmd.append(f"--include-onefile-external-data={k}={v}")
        for k in self.include_package_data:
            cmd.append(f"--include-package-data={k}")
        for k in self.noinclude_data_files:
            cmd.append(f"--noinclude-data-files={k}")

        # Add DLL options
        if self.list_package_dlls_var:
            cmd.append(f"--list-package-dlls={self.list_package_dlls_var}")
        if self.noinclude_dlls_var:
            cmd.append(f"--noinclude-dlls={self.noinclude_dlls_var}")
        if self.list_package_exe_var:
            cmd.append(f"--list-package-exe={self.list_package_exe_var}")

        # Add warning options
        if self.warn_implicit_exception_var:
            cmd.append("--warn-implicit-exception")
        if self.warn_unusual_code_var:
            cmd.append("--warn-unusual-code")
        if self.assume_yes_for_downloads_var:
            cmd.append("--assume-yes-for-downloads")
        if self.nowarn_mnemonic_var:
            cmd.append(f"--nowarn-mnemonic={self.nowarn_mnemonic_var}")

        # Add run options
        if self.run_var:
            cmd.append("--run")
        if self.debugger_var:
            cmd.append("--debugger")

        # Add compile options
        if self.full_compat_var:
            cmd.append("--full-compat")
        if self.file_reference_choice_var:
            cmd.append(f"--file-reference-choice={self.file_reference_choice_var}")
        if self.module_name_choice_var:
            cmd.append(f"--module-name-choice={self.module_name_choice_var}")
        if self.user_package_configuration_var:
            cmd.append(f"--user-package-configuration={self.user_package_configuration_var}")

        # Add output options
        if not self.remove_output_var:
            cmd.append("--no-remove-output")
        if self.no_pyi_file_var:
            cmd.append("--no-pyi-file")
        if self.output_filename_var:
            cmd.append(f"--output-filename={self.output_filename_var}")
        if self.output_dir_var:
            cmd.append(f"--output-dir={self.output_dir_var}")

        # Add deployment options
        if self.deployment_var == 2:
            cmd.append("--deployment-disable")
        elif self.deployment_var == 1:
            cmd.append("--deployment-partial")
            if self.no_deployment_flag_edit.text():
                 cmd.append(f"--no-deployment-flag={self.no_deployment_flag_edit.text()}")

        # Add debug options
        if self.debug_var:
            cmd.append("--debug")
        if self.unstripped_var:
            cmd.append("--unstripped")
        if self.trace_execution_var:
            cmd.append("--trace-execution")
        if self.xml_filename_var:
            cmd.append(f"--xml={self.xml_filename_var}")
        if self.low_memory_var:
            cmd.append("--low-memory")

        # Add C compiler options
        if self.C_complier_var:
            cmd.append(f"--{self.C_complier_var}")
        if self.msvc_version_var and self.C_complier_var == 'msvc':
            # Note: Nuitka might handle MSVC version differently, this is a placeholder
            pass 
        if self.jobs_var != 'auto':
            cmd.append(f"--jobs={self.jobs_var}")
        if self.lto_var != 'auto':
            cmd.append(f"--lto={self.lto_var}")
        if self.static_libpython_var != 'auto':
            cmd.append(f"--static-libpython={self.static_libpython_var}")
        if self.cf_protection_var != 'auto':
            cmd.append(f"--cf-protection={self.cf_protection_var}")

        # Add OS options
        if self.windows_uac_admin_var:
            cmd.append("--windows-uac-admin")
        if self.windows_uac_uiaccess_var:
            cmd.append("--windows-uac-uiaccess")
        if self.windows_console_mode_var:
            cmd.append(f"--windows-console-mode={self.windows_console_mode_var}")
        for ico_path in self.windows_icon_from_ico:
            cmd.append(f"--windows-icon-from-ico={ico_path}")
        if self.linux_icon_edit.text():
            cmd.append(f"--linux-icon={self.linux_icon_edit.text()}")

        # Add info options
        if self.company_name_var:
            cmd.append(f"--windows-company-name={self.company_name_var}")
        if self.product_name_var:
            cmd.append(f"--windows-product-name={self.product_name_var}")
        if self.file_version_var:
            cmd.append(f"--windows-file-version={self.file_version_var}")
        if self.product_version_var:
            cmd.append(f"--windows-product-version={self.product_version_var}")
        if self.copyright_text_var:
            cmd.append(f"--windows-copyright={self.copyright_text_var}")
        if self.trademarks_var:
            cmd.append(f"--windows-trademarks={self.trademarks_var}")

        # Add plugin options
        for plugin, enabled in self.plugin_vars.items():
            if enabled:
                cmd.append(f"--enable-plugin={plugin.replace('_', '-')}")
        if self.user_plugin_edit.text():
            cmd.append(f"--user-plugin={self.user_plugin_edit.text()}")

        command_str = ' '.join(cmd)
        if dry_run:
            self.command_display.setPlainText(command_str)
            self.status_bar.showMessage("构建命令已生成", 3000)
        else:
            return cmd

    def start_compile(self):
        cmd = self.get_command(dry_run=False)
        if not cmd:
            return # Error message already shown in get_command

        # Disable buttons during compilation
        self.btn_start_compile.setEnabled(False)
        self.btn_gen_command.setEnabled(False)

        # Clear console and show command
        self.console_display.clear()
        system_info = f'OS: {platform.platform()}, User@Host: {os.getenv("USERNAME", os.getenv("USER", "unknown"))}@{socket.gethostname()}'
        self.append_to_console(f"--- Compilation Started ---\nSystem: {system_info}\nCommand: {' '.join(cmd)}\n\n")
        self.status_bar.showMessage("编译进行中...")

        # Start worker thread
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(lambda: self.worker.run_command(cmd))
        # Signals are already connected in __init__

        self.worker_thread.start()

    def append_to_console(self, text):
        self.console_display.moveCursor(self.console_display.textCursor().End)
        self.console_display.insertPlainText(text)
        self.console_display.moveCursor(self.console_display.textCursor().End)

    def append_error_to_console(self, text):
        cursor = self.console_display.textCursor()
        cursor.movePosition(cursor.End)
        format = cursor.charFormat()
        format.setForeground(Qt.red) # Set text color to red for errors
        cursor.setCharFormat(format)
        cursor.insertText(text)
        cursor.setCharFormat(self.console_display.currentCharFormat()) # Reset to default
        self.console_display.setTextCursor(cursor)

    def on_compile_finished(self, return_code):
        # Re-enable buttons
        self.btn_start_compile.setEnabled(True)
        self.btn_gen_command.setEnabled(True)

        if return_code == 0:
            self.status_bar.showMessage("编译成功！", 5000)
        else:
            self.status_bar.showMessage(f"编译失败，返回码: {return_code}", 5000)

        # Stop and clean up the thread
        self.worker.stop()
        self.worker_thread.quit()
        self.worker_thread.wait()


def main():
    app = QApplication(sys.argv)
    window = NuitkaGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
