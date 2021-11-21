import sys
import threading
import worker
from typing import Optional
import time
import os

class ThreadTranslator:
    translated_dir = './translated'

    def __init__(self):
        self.file = None
        self.googlehandler = worker.LineHandler('ja', mode="GN")
        self.papagohandler = worker.LineHandler('ja', mode="PN")
        self.pron_handler = worker.LineHandler('ja', mode='XB')
        self.status=0
        self.done_code=300

    def _initalize_list(self):
        self.google_list = []
        self.papago_list = []
        self.pron_list = []
        self.is_translated_idx_list = []
        self.origin_lines = []
        self.actual_trans_list = []

    def _handle(self, handler:worker.LineHandler, text_list, pron:bool=False, renew_translated=False):
        self.status += 1
        for idx, line in enumerate(self.origin_lines):
            print(f"{idx}/{len(self.origin_lines)} 작업중")
            res = handler.line(line)
            if pron:
                text_list.append(res.origin_pronounce)
            else:
                if res.is_translated():
                    text_list.append(res.translated_line)
                    if renew_translated:
                        self.is_translated_idx_list.append(idx)
                else:
                    text_list.append(line)


        print(f"{handler.mode} 행수:", len(text_list))
        self.status += 100

    def run(self, file):
        self.file = file
        self._initalize_list()
        with open(self.file, 'r', encoding='utf-8-sig') as f:
            self.origin_lines = f.read().split('\n')
            self.actual_trans_list = self.origin_lines.copy()
            print("원본 행수:", len(self.origin_lines))
            th1 = threading.Thread(target=self._handle,
                                   args=(self.googlehandler, self.google_list, False, True))
            th2 = threading.Thread(target=self._handle,
                                   args=(self.papagohandler, self.papago_list, False, False))
            th3 = threading.Thread(target=self._handle,
                                   args=(self.pron_handler, self.pron_list, True, False))
            th1.start()
            th2.start()
            th3.start()

    def save(self):
        try:
            with open(os.path.join(self.translated_dir, os.path.basename(self.file)), 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(self.actual_trans_list))
            return True
        except:
            return False

    def _debug_save(self):
        with open("./goo.txt", "w", encoding='utf-8-sig') as f:
            f.write('\n'.join(self.google_list))
        with open("./pap.txt", "w", encoding='utf-8-sig') as f:
            f.write('\n'.join(self.papago_list))
        with open("./a5xs.txt", "w", encoding='utf-8-sig') as f:
            f.write('\n'.join(self.pron_list))

    def auto_papago(self, dir_path):
        if not os.path.isdir(self.translated_dir):
            os.makedirs(self.translated_dir)

        failed = []
        for file in os.listdir(dir_path):
            print(f"{os.path.basename(file)} 작업중...")
            # try
            self.file = file
            self._initalize_list()
            with open(os.path.join(dir_path, self.file), 'r', encoding='utf-8-sig') as f:
                self.origin_lines = f.read().split('\n')
                self.actual_trans_list = self.origin_lines.copy()
                print("원본 행수:", len(self.origin_lines))
                self._handle(self.googlehandler, self.papago_list, False, False)
                print(f"{os.path.basename(file)} 번역완료")
            with open(os.path.join(self.translated_dir, os.path.basename(file)), "w", encoding='utf-8-sig') as f:
                f.write('\n'.join(self.papago_list))
                print(f"{os.path.basename(file)} 저장완료")
            # except:
            #     failed.append(file)
            #     print(f"{os.path.basename(file)} 실패")
            #     print(sys.exc_info())

        if failed:
            for file in failed:
                print(os.path.basename(file), " 실패")
            input("종료")
        else:
            input("전부 완료.")


if __name__ == '__main__':
    dir_path= ''
    if len(sys.argv) == 2:
        dir_path = sys.argv[1]
    elif len(sys.argv) == 1:
        dir_path = input("디렉토리경로:")
    else:
        print("명령행 인자 잘못됨")
        exit(0)
    if dir_path:
        ThreadTranslator().auto_papago(dir_path)