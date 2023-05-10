import os
import re
import tkinter as tk
import socket
import tkinter.messagebox as mb
import threading
import datetime
import pygame
import time
from os import environ
from PIL import Image, ImageTk


class Server:
    myround = 0  # 我的回合
    round = 0  # 所有回合
    count = 0  # 计数是否达到五颗
    start = 0  # start=1方可下棋
    case = 0
    number = 1  # 允许的悔棋次数
    mychessnumber = 0
    play = 0
    emoji_list = ['🐻', '🗿', '🙃', '😊', '✔',
                  '🥰', '🤬', '🥶', '🥵', '😳',
                  '🤮', '🤩', '🤓', '😝', '🌚',
                  '🙈', '🤪', '🏩', '🚸', '🤺',
                  '🚾', '🉑', '🉐', '㊙', '🈶',
                  '🈚', '🆘', '🆗', '🤟',
                  '👊', '😭', '🙏', '🙌', '🦓',
                  '🦜', '🦄', '🎃', ]
    dirty = ['fuck', '狗日的', "日你妈", '我草', '仙人板板', '操你', '草你', '犊子', '你妈逼', '妈逼', "操你妈"]

    def __init__(self):
        self.root = tk.Tk()  # 主窗口
        self.root.geometry("1000x610")
        self.root.resizable(width=False, height=False)
        self.root.title("udp五子棋--server")
        self.create_widget()
        self.canva.bind("<Button-1>", self.running)
        self.inputtext.bind("<Key>", self.communicate)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.udp_socket.bind(('172.22.180.27', 10000))  # 绑定本机8081端口
        # self.address = ('153.3.61.115', 10000)
        self.udp_socket.bind(('127.0.0.1', 8081))  # 绑定本机8081端口
        self.address = ('127.0.0.1', 8080)
        self.start_receive()
        self.run()
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.mainloop()

    def run(self):
        self.Thread1 = threading.Thread(target=self.play_music)
        self.Thread1.start()

    def play_music(self):
        file_path = r"./英雄联盟 - 开天.mp3"
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(start=0.0)
        time.sleep(304)
        pygame.mixer.music.stop()

    def communicate(self, event):
        if event.keycode == 13:
            thread = threading.Thread(target=self.sendMsg)
            thread.start()

    def create_widget(self):
        self.canva = tk.Canvas(self.root, width=610, height=610, bg='#F9D65B')
        self.init_chessboard()
        self.canva.pack(side=tk.LEFT)
        self.label3 = tk.Label(self.root, text="黑子---我的回合", font={"微软雅黑", 12})
        self.label3.pack()
        self.Frame1 = tk.Frame(self.root)
        self.Frame1.pack()
        self.listbox1 = tk.Listbox(self.Frame1, width=30, height=8)
        self.listbox1.pack(side=tk.LEFT)
        self.label1 = tk.Label(self.root, text="游戏记录")
        self.label1.pack()
        self.Frame2 = tk.Frame(self.root)
        self.Frame2.pack()
        self.listbox2 = tk.Listbox(self.Frame2, width=51, height=12)
        self.listbox2.pack(side=tk.LEFT)
        self.label2 = tk.Label(self.root, text="聊天框")
        self.label2.pack()
        self.Frame3 = tk.Frame(self.root)
        self.Frame3.pack()
        self.inputtext = tk.Text(self.Frame3, width=51, height=8)
        self.inputtext.pack(side=tk.LEFT)
        self.scrollbar1 = tk.Scrollbar(self.Frame1)
        self.scrollbar1.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox1.config(yscrollcommand=self.scrollbar1.set)
        self.scrollbar1.config(command=self.listbox1.yview)
        self.scrollbar2 = tk.Scrollbar(self.Frame2)
        self.scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox2.config(yscrollcommand=self.scrollbar2.set)
        self.scrollbar2.config(command=self.listbox2.yview)
        self.scrollbar3 = tk.Scrollbar(self.Frame3)
        self.scrollbar3.pack(side=tk.RIGHT, fill=tk.Y)
        self.inputtext.config(yscrollcommand=self.scrollbar3.set)
        self.scrollbar3.config(command=self.inputtext.yview)

        # 主要下棋功能按钮，包括认输，悔棋，等等。。。
        self.button1 = tk.Button(self.root, text="发送信息", command=self.sendMsg)
        self.button1.place(x=923, y=555)
        self.button2 = tk.Button(self.root, text="退出游戏", command=self.exit)
        self.button2.place(x=618, y=555)
        self.button3 = tk.Button(self.root, text="表情 🤺", command=self.showFrame4)
        self.button3.place(x=865, y=555)
        self.button4 = tk.Button(self.root, text="认输", width=6, command=self.submit_to)
        self.button4.place(x=680, y=555)
        self.button5 = tk.Button(self.root, text="悔棋", width=6, command=self.regret)
        self.button5.place(x=735, y=555)
        self.listbox1.insert(tk.END, "正在连接Client,请稍后...")
        self.listbox1.see(tk.END)

        # 表情布局
        self.Frame4 = tk.Frame(self.root, width=150, height=200)
        self.button_list = [tk.Button(self.Frame4, text=self.emoji_list[i], width=2, height=1) for i in range(37)]
        for i in range(37):
            self.button_list[i].grid(row=i // 6, column=i - i // 6 * 6)
            self.button_list[i].bind("<Button-1>", self.add_to_text)

        # 头像图片设置
        image = Image.open("海绵宝宝.jpg")
        image = image.resize((145, 145))
        pyt = ImageTk.PhotoImage(image)
        label = tk.Label(self.Frame1, image=pyt)
        label.image = pyt  # 要重新进行赋值
        label.pack(side=tk.RIGHT)

        self.sound = Image.open("有.jpg")
        self.sound = self.sound.resize((23, 23))
        self.sound = ImageTk.PhotoImage(self.sound)
        self.button6 = tk.Button(image=self.sound, command=self.play_noplay)
        self.button6.image = self.sound
        self.button6.place(x=795, y=555)

        self.nosound = Image.open("无.jpg")
        self.nosound = self.nosound.resize((23, 23))
        self.nosound = ImageTk.PhotoImage(self.nosound)
        self.button7 = tk.Button(image=self.nosound, command=self.play_noplay)
        self.button7.image = self.nosound

    def play_noplay(self):
        if self.play == 0:
            pygame.mixer.music.pause()
            self.button6.place_forget()
            self.button7.place(x=795, y=555)
            self.play = 1
        else:
            self.play = 0
            pygame.mixer.music.unpause()
            self.button7.place_forget()
            self.button6.place(x=795, y=555)

    def regret(self):
        if self.mychessnumber:
            if self.round == 0:
                mb.showinfo(title="提示", message="对方已经落子，无法悔棋")
            else:
                if self.number:
                    answer = mb.askokcancel(title="提示", message="向对方提出悔棋请求")
                    if answer:
                        self.udp_socket.sendto("regret".encode("utf-8"), self.address)
                else:
                    mb.showinfo(title="提示", message="本局游戏悔棋次数已达上限！")
        else:
            mb.showinfo(title="提示", message="棋子不存在，无法悔棋")

    def submit_to(self):
        answer = mb.askokcancel(title="消息提示框", message="您真的要认输吗？")
        if answer:
            self.udp_socket.sendto("submit_to|".encode("utf-8"), self.address)
            self.lose()

    def win(self):
        mb.showinfo(title="提示", message="恭喜你，你赢得了这场游戏")
        self.listbox1.insert(tk.END, "Server获胜")
        self.listbox1.see(tk.END)

    def lose(self):
        self.listbox1.insert(tk.END, "Client获胜")
        self.listbox1.see(tk.END)
        mb.showinfo(title="游戏结果", message="很遗憾,您输掉了这场游戏")

    def showFrame4(self):
        if self.case == 0:
            self.Frame4.place(x=815, y=346)
            self.case = 1
        else:
            self.Frame4.place_forget()
            self.case = 0

    def add_to_text(self, event):
        self.inputtext.insert(tk.END, event.widget["text"])
        self.showFrame4()

    def sendMsg(self):
        dt = datetime.datetime.now()
        text = self.inputtext.get('0.0', tk.END)
        text = re.sub("|".join(self.dirty), "***", text)
        if text.isspace():
            mb.showinfo(title="提示", message="不能发送空白消息")
            self.inputtext.delete("0.0", tk.END)
        else:
            self.udp_socket.sendto(("message|" + text).encode("utf-8"), self.address)
            self.listbox2.insert(tk.END, "Server   time:" + dt.strftime("%Y-%m-%d %H:%M:%S \n"))
            self.listbox2.insert(tk.END, text)
            self.listbox2.see(tk.END)
            self.inputtext.delete("0.0", tk.END)

    def exit(self):
        self.udp_socket.sendto("exit".encode("utf-8"), self.address)
        pygame.mixer.music.stop()
        # self.root.destroy()
        os._exit(0)

    def init_chessboard(self):
        self.number = 1
        for i in range(15):
            self.canva.create_line(20, i * 40 + 20, 580, 20 + 40 * i, fill='black')
            self.canva.create_line(i * 40 + 20, 20, 20 + 40 * i, 580, fill='black')
        self.canva.create_oval(136, 136, 144, 144, fill="black")
        self.canva.create_oval(296, 296, 304, 304, fill="black")
        self.canva.create_oval(456, 456, 464, 464, fill="black")
        self.canva.create_oval(136, 456, 144, 464, fill="black")
        self.canva.create_oval(456, 136, 464, 144, fill="black")
        self.map = [[" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "] for i in range(15)]

    def receive_Msg(self):
        while True:
            data, address = self.udp_socket.recvfrom(1024)
            data = data.decode("utf-8")
            a = data.split("|")
            if not data:
                mb.showinfo("client has exited")
                break
            elif a[0] == "join":
                self.start = 1
                self.listbox1.insert(tk.END, "连接成功，可以开始游戏")
                self.udp_socket.sendto("success|".encode("utf-8"), self.address)
            elif a[0] == "exit":
                mb.showinfo(title="Message prompt box", message="client has exited the game,about to exit the program")
                self.exit()
            elif a[0] == "over":
                self.lose()
            elif a[0] == "message":
                dt = datetime.datetime.now()
                self.listbox2.insert(tk.END, "Client   time:" + dt.strftime("%Y-%m-%d %H:%M:%S \n"))
                self.listbox2.insert(tk.END, a[1])
                self.listbox2.see(tk.END)
            elif a[0] == "move":
                data = a[1].split(",")
                x = int(data[0])
                y = int(data[1])
                self.listbox1.insert(tk.END, "Client play chess on x:{0},y:{1}".format(x, y))
                self.listbox1.see(tk.END)
                self.draw_chess(x, y, "white")
                self.map[x][y] = str(1)
                self.round_mine()
            elif a[0] == "success":
                self.listbox1.insert(tk.END, "成功连接")
                self.start = 1
            elif a[0] == "remake":
                mb.showinfo(title="提示", message="对方选择继续游戏")
                self.remake()
            elif a[0] == "submit_to":
                mb.showinfo(title="提示", message="对方认输")
                self.win()
            elif a[0] == "regret":
                answer = mb.askokcancel(title="提示", message="对方提出悔棋，是否同意")
                self.udp_socket.sendto(("regret_answer|" + str(answer)).encode("utf-8"), self.address)
            elif a[0] == "regret_number":
                self.round_opposite()
                self.canva.delete(self.lastchess)
                self.map[self.x][self.y] = " "
                self.listbox1.insert(tk.END, "Client悔棋 x:{0},y:{1}".format(self.x, self.y))
                self.listbox1.see(tk.END)
            elif a[0] == "regret_answer":
                if bool(a[0]):
                    mb.showinfo(title="提示", message="对方同意悔棋")
                    self.canva.delete(self.lastchess)
                    self.number = 0
                    self.round_mine()
                    self.map[self.x][self.y] = " "
                    self.listbox1.insert(tk.END, "Server悔棋 x:{0},y:{1}".format(self.x, self.y))
                    self.listbox1.see(tk.END)
                    self.udp_socket.sendto("regret_number|".encode("utf-8"), self.address)
                else:
                    mb.showinfo(title="提示", message="落子无悔！对方不同意悔棋。")

        self.udp_socket.close()

    def remake(self):
        self.canva.delete(tk.ALL)
        self.init_chessboard()

    def start_receive(self):
        thread = threading.Thread(target=self.receive_Msg)
        thread.setDaemon(True)
        thread.start()

    def running(self, event):
        if self.start == 0:
            mb.showinfo(title="提示", message="连接未成功，请稍后。。。")
        else:
            if self.myround != self.round:
                mb.showinfo(title="提示", message="现在是对方的回合")
                return
            x = event.x // 40  # 整数除法
            y = event.y // 40
            if self.map[x][y] != " ":
                mb.showinfo(title="提示", message="此处已有棋子")
            else:
                self.draw_chess(x, y, 'black')
                self.mychessnumber += 1
                self.listbox1.insert(tk.END, "Server play chess on x:{0},y:{1}".format(x, y))
                data = str(x) + "," + str(y)
                self.map[x][y] = str(0)
                self.send("move|" + data)
                if self.check_win_lose(x, y):
                    self.send("over|")
                    self.win()
                self.round_opposite()

    def round_mine(self):
        self.round = 0
        self.label3["text"] = "黑子---我的回合"

    def round_opposite(self):
        self.round = 1
        self.label3["text"] = "白子---对手回合，等待对手落子。。。"

    def draw_chess(self, x, y, color):
        self.lastchess = self.canva.create_oval(10 + x * 40, 10 + y * 40, 30 + x * 40, 30 + y * 40, fill=color)
        self.x = x
        self.y = y

    def send(self, data):
        self.udp_socket.sendto(data.encode("utf-8"), self.address)

    def check_win_lose(self, x, y):
        for i in range(-4, 5):
            if 14 >= x + i >= 0 and 14 >= y + i >= 0:
                if self.map[x + i][y + i] == "0":
                    self.count += 1
                    if self.count == 5:
                        return True
                else:
                    self.count = 0
        self.count = 0
        for i in range(-4, 5):
            if 14 >= y + i >= 0:
                if self.map[x][y + i] == "0":
                    self.count += 1
                    if self.count == 5:
                        return True
                else:
                    self.count = 0
        self.count = 0
        for i in range(-4, 5):
            if 14 >= x + i >= 0:
                if self.map[x + i][y] == "0":
                    self.count += 1
                    if self.count == 5:
                        return True
                else:
                    self.count = 0
        self.count = 0
        for i in range(-4, 5):
            if 14 >= x - i >= 0 and 0 <= y + i <= 14:
                if self.map[x - i][y + i] == "0":
                    self.count += 1
                    if self.count == 5:
                        return True
                else:
                    self.count = 0
        self.count = 0
        return False


if __name__ == '__main__':
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    gui = Server()
