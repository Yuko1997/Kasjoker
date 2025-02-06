import os
import time
import configparser
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 读取 path.ini 获取目标文件路径
config = configparser.ConfigParser()
config.read('path.ini')

try:
    target_file = config.get('Paths', 'target_file')
except (configparser.NoSectionError, configparser.NoOptionError):
    print("path.ini 格式错误")
    exit(1)

# 提取目录和文件名
target_dir = os.path.dirname(target_file)
target_filename = os.path.basename(target_file)

# 定义文件系统事件处理器
class TargetFileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if os.path.basename(event.src_path) == target_filename:
            print(f"文件已创建: {event.src_path}")
            self.replace_file()

    def on_modified(self, event):
        if os.path.basename(event.src_path) == target_filename:
            print(f"文件已修改: {event.src_path}")
            self.replace_file()

    def on_moved(self, event):
        if os.path.basename(event.dest_path) == target_filename or os.path.basename(event.src_path) == target_filename:
            print(f"文件已重命名或移动: {event.src_path} -> {event.dest_path}")
            self.replace_file()

    def replace_file(self):
        source_dll = os.path.join(os.getcwd(), 'cbi.dll')
        if os.path.exists(source_dll):
            try:
                shutil.copy2(source_dll, target_dir)
                print(f"已成功覆盖 cbi.dll 到 {target_dir}")
                observer.stop()  # 替换成功后停止监控
            except Exception as e:
                print(f"覆盖文件时出错: {e}")
        else:
            print("源文件 cbi.dll 不存在，无法覆盖。")

# 初始化 watchdog 观察者
observer = Observer()
event_handler = TargetFileEventHandler()

# 如果目录不存在，等待目录创建
while not os.path.exists(target_dir):
    print(f"等待目录创建: {target_dir}")
    time.sleep(0.3)

observer.schedule(event_handler, path=target_dir, recursive=False)

try:
    print(f"开始监控文件: {target_file}")
    observer.start()
    while observer.is_alive():
        time.sleep(0.3)
except KeyboardInterrupt:
    observer.stop()
    print("停止")

observer.join()
