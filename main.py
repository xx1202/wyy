import csv
import threading
import tkinter as tk
from tkinter import messagebox, ttk

# from ttkbootstrap import Style

from spider import Spider
from data import Comments
import json


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("网易云评论爬虫")
        self.root.geometry("500x500")  # 设置窗口大小

        self.progress_label = None
        self.progress = None
        self.show_initial_screen()

    def clear_screen(self):
        """清除当前界面"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_initial_screen(self):
        """显示选择操作的界面"""
        self.clear_screen()

        # 创建选择操作按钮
        self.label = tk.Label(self.root, text="请选择操作：")
        self.label.pack(pady=10)

        self.button1 = tk.Button(self.root, text="爬取评论", command=self.show_input_screen_for_crawl)
        self.button1.pack(pady=10)

        self.button2 = tk.Button(self.root, text="查看评论", command=self.show_input_screen_for_query)
        self.button2.pack(pady=10)

    def show_input_screen_for_crawl(self):
        """显示爬取评论输入框"""
        self.clear_screen()

        # 显示标签和输入框
        self.label = tk.Label(self.root, text="请输入要爬取评论的音乐 ID:")
        self.label.pack(pady=10)

        self.music_id_entry = tk.Entry(self.root, width=40)
        self.music_id_entry.pack(pady=10)

        self.label = tk.Label(self.root, text="请输入要爬取评论的页数:")
        self.label.pack(pady=10)

        self.page_entry = tk.Entry(self.root, width=40)
        self.page_entry.pack(pady=10)

        # 提交按钮
        self.submit_button = tk.Button(self.root, text="提交", command=self.crawl_comments)
        self.submit_button.pack(pady=20)

        # 返回选择操作按钮
        self.back_button = tk.Button(self.root, text="返回", command=self.show_initial_screen)
        self.back_button.pack(pady=10)

    def show_input_screen_for_query(self):
        """显示查看评论输入框"""
        self.clear_screen()

        # 显示标签和输入框
        self.label = tk.Label(self.root, text="请输入要查看的数量")
        self.label.pack(pady=10)

        self.find_num_entry = tk.Entry(self.root, width=40)
        self.find_num_entry.pack(pady=10)

        # 提交按钮
        self.submit_button = tk.Button(self.root, text="提交", command=self.query_comments)
        self.submit_button.pack(pady=20)

        # 返回选择操作按钮
        self.back_button = tk.Button(self.root, text="返回", command=self.show_initial_screen)
        self.back_button.pack(pady=10)

    def crawl_comments(self):
        """爬取评论操作"""
        music_id = self.music_id_entry.get()
        page = self.page_entry.get()
        if music_id and page:
            # 启动爬取任务的后台线程
            threading.Thread(target=self.run_crawl, args=(music_id, int(page)), daemon=True).start()
        else:
            messagebox.showwarning("警告", "请输入有效的音乐 ID 和页数！")

    def run_crawl(self, music_id, page):
        """爬取评论，并更新GUI"""
        self.show_progress()
        try:
            spider = Spider()
            data = spider.get_comments(music_id, page)
            self.progress_label.config(text="爬取完成!")
            self.progress.stop()
            self.progress["value"] = 100
            self.handle_crawl_success(data)
        except Exception as e:
            self.progress.stop()
            self.progress_label.config(text="爬取失败")
            messagebox.showerror("错误", f"爬取过程中发生错误: {e}")

    def handle_crawl_success(self, data):
        """处理爬取成功后的操作"""
        # 在原页面上添加存储选项
        self.label.config(text="爬取成功！请选择存储方式：")

        # 创建三个按钮供用户选择
        self.db_button = tk.Button(self.root, text="存入数据库", command=lambda: self.process_choice('database', data))
        self.db_button.pack(pady=10)

        self.file_button = tk.Button(self.root, text="保存为文件", command=lambda: self.process_choice('file', data))
        self.file_button.pack(pady=10)

    def process_choice(self, choice, data):
        """处理用户选择的存储方式"""
        if choice == 'database':
            self.save_to_database(data)
        else:
            self.save_to_file(data)

    def save_to_database(self, data):
        """将数据存入数据库"""
        try:
            comm = Comments()
            comm.insert(data)
            messagebox.showinfo("成功", "评论已成功存入数据库！")
        except Exception as e:
            messagebox.showerror("错误", f"存入数据库时发生错误: {e}")
        finally:
            self.show_initial_screen()

    def save_to_file(self, data):
        """将数据保存为文件"""
        try:
            with open("comments.csv", "w", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["用户名", "评论内容", "评论时间", "点赞数"])
                writer.writerows(data)
            messagebox.showinfo("成功", "评论已成功保存为文件！")
        except Exception as e:
            messagebox.showerror("错误", f"保存为文件时发生错误: {e}")
        finally:
            self.show_initial_screen()

    def show_progress(self):
        """显示进度条和状态标签"""
        if self.progress_label is None:
            self.progress_label = tk.Label(self.root, text="正在爬取评论...")
            self.progress_label.pack(pady=10)
        if self.progress is None:
            self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
            self.progress["maximum"] = 100
            self.progress["value"] = 0
            self.progress.pack(pady=10)

    def show_comments_table(self, data):
        """使用 Treeview 显示查询结果"""
        self.clear_screen()

        # 创建标题栏
        self.label = tk.Label(self.root, text="查询结果:")
        self.label.pack(pady=10)

        # 创建 Treeview 表格
        self.tree = ttk.Treeview(self.root, columns=("用户名", "评论内容", "点赞数"), show="headings")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # 定义表头
        self.tree.heading("用户名", text="用户名")
        self.tree.heading("评论内容", text="评论内容")
        self.tree.heading("点赞数", text="点赞数")

        # 定义列宽度
        self.tree.column("用户名", width=100)
        self.tree.column("评论内容", width=300)
        self.tree.column("点赞数", width=50)

        # 插入数据到表格
        for comment in data:
            self.tree.insert("", tk.END, values=(comment["username"], comment["content"], comment["likes"]))

        # 创建返回按钮
        self.back_button = tk.Button(self.root, text="返回", command=self.show_initial_screen)
        self.back_button.pack(pady=10)

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def query_comments(self):
        """查看评论操作"""
        find_num = self.find_num_entry.get()
        if find_num:
            comm = Comments()
            data = comm.select(num=int(find_num))
            if data:
                self.show_comments_table(data)
            else:
                messagebox.showinfo("查询结果", "未找到相关评论。")
        else:
            messagebox.showwarning("警告", "请输入一个有效的数量！")


# 创建主窗口
root = tk.Tk()
# style = Style(theme='minty')
# TOP6 = style.master
# 创建应用实例
app = App(root)

# 运行主循环
root.mainloop()