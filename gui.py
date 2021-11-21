import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import os
import worker
import threading_translator
import sys
import tkinter.filedialog

class Gui:
    translated_dir_path = "./translated"

    def __init__(self):
        self.file = None
        self.translate_mode = 'G'
        self.pronunciation_mode = True
        self.init_complete=False
        self.saved = False

        self.mf = tk.Tk()
        self.mf.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._initialize_string_vars()
        self._make()
        self._key_bind()

        self.text_controller = Textcontroller(self)
        self._set_message_queue()

    def _set_message_queue(self):
        self._message_time = 0
        self.msg_after_value = None
        self.message=''

    def _renew_message(self):
        if self._message_time < 30:
            self.message_var.set(self.message)
            self._message_time += 1
            self.msg_after_value = self.mf.after(100, self._renew_message)
        else:
            self.message_var.set('')

    def show_message(self, msg):
        if self.msg_after_value:
            self.mf.after_cancel(self.msg_after_value)
        self._message_time = 0
        self.message = msg
        self._renew_message()

    def _load_text_when_open(self):
        if not self.init_complete:
            self.init_complete = self.text_controller.renew_text()
            if not self.init_complete and self.text_controller.is_translating_completed():
                if msgbox.askyesno("저장할까요", "번역할 내용이 없습니다. 그대로 저장할까요?"):
                    self.command_save()
                else:
                    exit(0)
            self.mf.after(100, self._load_text_when_open)

    def _initialize_string_vars(self):
        self.google_btn_text_variable = tk.StringVar()
        self.papago_btn_text_variable = tk.StringVar()
        self.row_count_string = tk.StringVar()
        self.row_count_string.set("로드중....")
        self.file_name = tk.StringVar()
        self.file_name.set(self.file)
        self.start_language_text = tk.StringVar()
        self.start_language_text.set("원본")
        self.dest_language_text = tk.StringVar()
        self.dest_language_text.set("번역")
        self.start_language_pronunciation = tk.StringVar()
        self.start_language_pronunciation.set("발음")
        self.message_var = tk.StringVar()
        self.google_btn_text_variable.set("√ 구글 번역")
        self.papago_btn_text_variable.set("파파고 번역")

    def _make(self):
        self.mf.title("스크립트 번역 저장 툴")
        self.mf.resizable(0, 0)
        self.default_bg_color = '#cccccc'
        self.mf.config(bg=self.default_bg_color)
        self._make_header_frame()
        self._make_translate_frame()
        self._make_bottom_right()
        self._make_bottom_left()

    def _make_header_frame(self):
        header_frame = tk.Frame(self.mf, bd=5, bg=self.default_bg_color)
        header_frame.pack(fill='x', side='top')
        tk.Label(header_frame, textvariable=self.row_count_string, bg=self.default_bg_color).pack(fill='x', side='left')
        tk.Label(header_frame, textvariable=self.file_name, bg=self.default_bg_color).pack(side='right')

    def _make_translate_frame(self):
        translate_frame = tk.Frame(self.mf, bd=5, bg=self.default_bg_color)
        translate_frame.pack(fill='x', side='top')
        tk.Label(translate_frame, textvariable=self.start_language_text, bg=self.default_bg_color).grid(
            row=0, column=0, sticky='w', padx=4
        )
        translate_title_frame = tk.Frame(translate_frame, bg=self.default_bg_color)
        translate_title_frame.grid(row=0, column=1, sticky='ew')
        tk.Label(translate_title_frame, textvariable=self.dest_language_text, bg=self.default_bg_color).pack(
            side='left', anchor='w', expand=True, pady=4, padx=5
        )

        tk.Button(
            translate_title_frame, textvariable=self.papago_btn_text_variable, width=16, bg='#aaffaa',
            command=self.command_papago_trans,
        ).pack(side='right', pady=5, padx=5)
        tk.Button(
            translate_title_frame, textvariable=self.google_btn_text_variable, width=16, bg='#ffaaaa',
            command=self.command_google_trans
        ).pack(side='right', pady=5, padx=5)

        original_text_frame = tk.Frame(translate_frame, bg=self.default_bg_color)
        original_text_frame.grid(row=1, column=0, padx=5)
        self.original_text = tk.Text(original_text_frame, bg='#eee', width=70, height=9)
        self.original_text.config(state='disabled')
        self.original_text.pack(side='left')
        original_text_scrbar = tk.Scrollbar(original_text_frame)
        original_text_scrbar.pack(side='right', fill='y')
        original_text_scrbar.config(command=self.original_text.yview)
        self.original_text.config(yscrollcommand=original_text_scrbar.set)

        translated_text_frame = tk.Frame(translate_frame)
        translated_text_frame.grid(row=1, column=1, padx=5, rowspan=2, sticky='n')
        self.translated_text = tk.Text(translated_text_frame, width=70, height=14)
        self.translated_text.config(undo=True, maxundo=50)
        self.translated_text.pack(side='left')
        translated_text_scrbar = tk.Scrollbar(translated_text_frame)
        translated_text_scrbar.pack(side='right', fill='y')
        translated_text_scrbar.config(command=self.translated_text.yview)
        self.translated_text.config(yscrollcommand=translated_text_scrbar.set)

        tk.Label(translate_frame, textvariable=self.start_language_pronunciation, height=4, relief='groove',
                 anchor='nw', justify='left').grid(
            row=2, column=0, sticky='new', padx=5)

    def _make_bottom_right(self):
        btn_frame = tk.Frame(self.mf, bd=5, bg=self.default_bg_color)
        btn_frame.pack(side='right', anchor='e')
        #tk.Button(
        #    btn_frame, text="예약어 불러오기", width=16, bg='#fcab89', command=self.command_load_reserve
        #).grid(row=0, column=0, rowspan=3, sticky='ns', padx=5)

        self.prev_btn = tk.Button(btn_frame, text="이전 (Page Up)", width=16, bg='#fedcba', command=self.command_prev,
                                  takefocus=False)
        self.prev_btn.grid(
            row=2, column=1, sticky='w', padx=5
        )
        tk.Frame(btn_frame, height=5, takefocus=False, bg=self.default_bg_color).grid(row=1, column=1)
        self.next_btn = tk.Button(btn_frame, text="다음 (Page Down)", width=16, bg='#abcdef', command=self.command_next)
        self.next_btn.grid(
            row=0, column=1, sticky='w', padx=5
        )
        ttk.Separator(btn_frame, orient="vertical", takefocus=False).grid(
            row=0, column=2, rowspan=3, sticky='ns', padx=5
        )
        self.save_btn = tk.Button(btn_frame, text="작업 저장", width=16, bg='#fc8ab1', command=self.command_save)
        self.save_btn.grid(
            row=0, column=3, rowspan=3, sticky='ns', padx=5
        )

    def _make_bottom_left(self):
        left_frame = tk.Frame(self.mf, bg=self.default_bg_color)
        left_frame.pack(side='left', fill='y', padx=8)
        self.pronunciation_mode_var = tk.BooleanVar()
        chkbtn = tk.Checkbutton(left_frame, text='발음 표시', bg=self.default_bg_color, variable=self.pronunciation_mode_var,
                       activebackground=self.default_bg_color, command=self.command_balum)
        chkbtn.select()
        chkbtn.pack(side='top', anchor='w')
        tk.Label(left_frame, textvariable=self.message_var, bg=self.default_bg_color).pack(side='top', pady=5)

    def _key_bind(self):
        self.mf.bind('<Prior>', self.command_prev)
        self.mf.bind('<Next>', self.command_next)
        self.mf.bind('<Control-s>', self.command_save)
        self.mf.bind('<Control-g>', self.command_google_trans)
        self.mf.bind('<Control-p>', self.command_papago_trans)
        #self.mf.bind('<Control-r>', self.command_load_reserve)
        self.mf.bind('<Key>', self.need_saving)

    def need_saving(self, event=None):
        self.saved = False

    def set_original_line(self, text):
        self.original_text.config(state='normal')
        self.original_text.delete(1.0, "end")
        self.original_text.insert(1.0, text)
        self.original_text.config(state='disabled')

    def set_translated_line(self, text):
        self.translated_text.delete(1.0, "end")
        self.translated_text.insert(1.0, text)

    def get_translated_line(self):
        return self.translated_text.get(1.0, "end")

    def set_pronunciation_line(self, text):
        self.start_language_pronunciation.set(text)

    def command_load_reserve(self, event=None):
        worker.load_reserve(forced=True)

    def command_prev(self, event: tk.Event = None):
        if not self.text_controller.move_focus(-1):
            self.show_message("처음 문장입니다.")
        else:
            self.need_saving()

    def command_next(self, event=None):
        if not self.text_controller.move_focus(1):
            if self.text_controller.is_translating_completed():
                self.show_message("마지막 문장입니다.")
            else:
                self.show_message("다음문장이 번역중입니다.")
        else:
            self.need_saving()

    def command_save(self, event=None):
        if self.text_controller.save():
            self.show_message("저장하였습니다.")
            self.saved=True
        else:
            self.show_message("저장 실패")

    def command_google_trans(self, event=None):
        self.translate_mode = 'G'
        self.google_btn_text_variable.set("√ 구글 번역")
        self.papago_btn_text_variable.set("파파고 번역")
        self.need_saving()
        if not self.text_controller.renew_text():
            self.show_message("구글 번역을 불러오지 못했습니다.")

    def command_papago_trans(self, event=None):
        self.translate_mode = 'P'
        self.google_btn_text_variable.set("구글 번역")
        self.papago_btn_text_variable.set("√ 파파고 번역")
        self.need_saving()
        if not self.text_controller.renew_text():
            self.show_message("파파고 번역을 불러오지 못했습니다.")

    def command_balum(self, event=None):
        self.pronunciation_mode = self.pronunciation_mode_var.get()
        if not self.text_controller.renew_text():
            self.show_message("발음을 불러오지 못했습니다.")

    def _on_closing(self):
        if not self.saved:
            user_push = msgbox.askyesnocancel("저장 후 종료", "종료하기 전 저장하시겠습니까?")
            if user_push is None:
                return
            elif user_push:
                if self.text_controller.save():
                    msgbox.showinfo("저장 완료", f"{self.text_controller.thread_trans.translated_dir}에 저장했습니다.")
                else:
                    msgbox.showerror("오류", "저장 오류")
            else:
                pass
        self.mf.destroy()
        exit(0)

    def run(self, file):
        self.file = file
        self.mf.deiconify()
        if self.file:
            self.file_name.set(os.path.basename(self.file))
            self.text_controller.threading_start(self.file)
            self._load_text_when_open()
            self.mf.mainloop()
        else:
            exit(0)



class Textcontroller:
    def __init__(self, gui):
        self.gui = gui
        self.focus_idx = 0
        self.thread_trans = threading_translator.ThreadTranslator()

    def threading_start(self, file):
        self.thread_trans.run(file)

    def _insert_actual_text(self):
        actual_text = self.gui.get_translated_line().rstrip('\n')
        self.thread_trans.actual_trans_list[self.thread_trans.is_translated_idx_list[self.focus_idx]] = actual_text

    def renew_text(self):
        renew_trans = 'ERROR'
        renew_pron = ''
        try:
            if self.gui.translate_mode.upper() == 'G':
                renew_trans = self.thread_trans.google_list[self.thread_trans.is_translated_idx_list[self.focus_idx]]
            elif self.gui.translate_mode.upper() == 'P':
                renew_trans = self.thread_trans.papago_list[self.thread_trans.is_translated_idx_list[self.focus_idx]]
            if self.gui.pronunciation_mode:
                renew_pron = self.thread_trans.pron_list[self.thread_trans.is_translated_idx_list[self.focus_idx]]

            self.gui.set_original_line(
                self.thread_trans.origin_lines[self.thread_trans.is_translated_idx_list[self.focus_idx]]
            )
            self.gui.set_pronunciation_line(renew_pron)
            self.gui.set_translated_line(renew_trans)
            self.gui.row_count_string.set("{}/{} 행".format(
                self.thread_trans.is_translated_idx_list[self.focus_idx] + 1, len(self.thread_trans.origin_lines)
            ))
        except IndexError:
            return False
        return True

    def move_focus(self, move):
        if 0 <= self.focus_idx + move < len(self.thread_trans.is_translated_idx_list):
            self._insert_actual_text()
            self.focus_idx += move
            return self.renew_text()
        else:
            return False

    def save(self):
        self._insert_actual_text()
        return self.thread_trans.save()

    def is_translating_completed(self):
        return self.thread_trans.status >= self.thread_trans.done_code



if __name__ == '__main__':
    gui = Gui()
    file_path=''
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
    elif len(sys.argv) == 1:
        file_path = tkinter.filedialog.askopenfilename()
    else:
        msgbox.showerror("명령행 인자가 잘못되었다.")
        exit(0)
    if file_path:
        gui.run(file_path)

