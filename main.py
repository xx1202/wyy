import csv
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from spider import Spider
from data import Comments
import json


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("网易云评论爬虫")
        self.root.geometry("700x500")  # 设置窗口大小

        self.progress_label = None
        self.progress = None
        self.tree = None  # Initialize Treeview reference
        self.music_id_entry = None  # Initialize music_id_entry reference
        self.page_entry = None  # Initialize page_entry reference
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
        self.root.after(0, self.show_progress)
        try:
            spider = Spider()
            data = spider.get_comments(music_id, page)
            self.root.after(0, self.update_progress, "爬取完成!", 100)
            self.root.after(0, lambda: self.handle_crawl_success(data))
        except Exception as e:
            self.root.after(0, self.update_progress, "爬取失败", 0)
            self.root.after(0, lambda: messagebox.showerror("错误", f"爬取过程中发生错误: {e}"))

    def handle_crawl_success(self, data):
        """处理爬取成功后的操作"""
        # 在原页面上添加存储选项
        if self.label:
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
        if not self.progress_label:
            self.progress_label = tk.Label(self.root, text="正在爬取评论...")
            self.progress_label.pack(pady=10)

        if not self.progress:
            self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
            self.progress["maximum"] = 100
            self.progress["value"] = 0
            self.progress.pack(pady=10)

    def update_progress(self, text, value):
        """更新进度条和状态标签"""
        if self.progress_label and self.progress_label.winfo_exists():
            self.progress_label.config(text=text)
        if self.progress and self.progress.winfo_exists():
            self.progress.stop()
            self.progress["value"] = value

    def show_comments_table(self, data):
        """使用 Treeview 显示查询结果"""
        self.clear_screen()

        # 创建标题栏
        self.label = tk.Label(self.root, text="查询结果:")
        self.label.pack(pady=10)

        # 创建 Treeview 表格
        self.tree = ttk.Treeview(self.root, columns=("ID", "用户名", "评论内容", "点赞数", "评论时间"), show="headings")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # 定义表头
        self.tree.heading("ID", text="ID")
        self.tree.heading("用户名", text="用户名")
        self.tree.heading("评论内容", text="评论内容")
        self.tree.heading("点赞数", text="点赞数")
        self.tree.heading("评论时间", text="评论时间")

        # 定义列宽度
        self.tree.column("ID", width=50)
        self.tree.column("用户名", width=100)
        self.tree.column("评论内容", width=300)
        self.tree.column("点赞数", width=50)
        self.tree.column("评论时间", width=50)

        # 插入数据到表格
        for comment in data:
            self.tree.insert("", tk.END, values=(comment["id"], comment["username"], comment["content"], comment["likes"], comment["time"]))

        # 绑定右键菜单
        self.tree.bind("<Button-3>", self.show_context_menu)

        # 创建右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="修改评论", command=self.edit_comment)
        self.context_menu.add_command(label="删除评论", command=self.delete_comment)

        # 创建返回按钮
        self.back_button = tk.Button(self.root, text="返回", command=self.show_initial_screen)
        self.back_button.pack(pady=10)

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def show_context_menu(self, event):
        """显示右键菜单"""
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            self.context_menu.post(event.x_root, event.y_root)

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

    def edit_comment(self):
        """编辑选中的评论"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择一个评论进行修改！")
            return

        item = self.tree.item(selected_item)
        comment_data = item['values']

        # 创建新窗口进行编辑
        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑评论")
        edit_window.geometry("400x300")

        label = tk.Label(edit_window, text="编辑评论内容:")
        label.pack(pady=10)

        username_entry = tk.Entry(edit_window, width=40)
        username_entry.insert(0, comment_data[1])
        username_entry.pack(pady=10)

        content_entry = tk.Entry(edit_window, width=40)
        content_entry.insert(0, comment_data[2])
        content_entry.pack(pady=10)

        likes_entry = tk.Entry(edit_window, width=40)
        likes_entry.insert(0, comment_data[3])
        likes_entry.pack(pady=10)

        submit_button = tk.Button(edit_window, text="提交修改", command=lambda: self.update_comment(comment_data[0], selected_item, username_entry, content_entry, likes_entry, edit_window))
        submit_button.pack(pady=20)

    def update_comment(self, comment_id, item, username_entry, content_entry, likes_entry, edit_window):
        """更新评论内容"""
        updated_data = {
            "id": comment_id,
            "username": username_entry.get(),
            "content": content_entry.get(),
            "likes": likes_entry.get(),
            "time": self.tree.item(item, 'values')[4]  # 保持原始时间
        }

        try:
            comm = Comments()
            comm.update(data=updated_data, id=comment_id)  # 确保 Comments 类中存在 update 方法
            self.tree.item(item, values=(updated_data["id"], updated_data["username"], updated_data["content"], updated_data["likes"], updated_data["time"]))
            messagebox.showinfo("成功", "评论已成功修改！")
        except Exception as e:
            messagebox.showerror("错误", f"修改评论时发生错误: {e}")
        finally:
            edit_window.destroy()

    def delete_comment(self):
        """删除选中的评论"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择一个评论进行删除！")
            return

        item = self.tree.item(selected_item)
        comment_data = item['values']

        try:
            comm = Comments()
            comm.delete(comment_data[0])
            self.tree.delete(selected_item)
            messagebox.showinfo("成功", "评论已成功删除！")
        except Exception as e:
            messagebox.showerror("错误", f"删除评论时发生错误: {e}")


# 创建主窗口
root = tk.Tk()
# style = Style(theme='minty')
# TOP6 = style.master
# 创建应用实例
app = App(root)

# 运行主循环
root.mainloop()