import translator
from enum import Enum
import os

reserve_file_name = './reserve.txt'
reserve = {}
is_loaded = False


def load_reserve(forced=False):
    global is_loaded
    if (not is_loaded) or forced:
        print("reserve.txt 로드함")
        if not os.path.isfile(reserve_file_name):
            with open('./reserve.txt', 'w', encoding='utf-8-sig') as f:
                f.writelines(
                    ["#おはよう (#제거후 써주세요)\n", "#좋은아침\n"]
                )
        with open('./reserve.txt', 'r', encoding='utf-8-sig') as f:
            step = 0
            start_sentence = ''
            for line in f.read().split('\n'):
                if line.startswith('#'):
                    continue
                if line:
                    if step == 0:
                        start_sentence = line
                        step += 1
                    elif step == 1:
                        add_reserve(start_sentence, line)
                        step = 0
        is_loaded = True


def add_reserve(start_sentence, dest_sentence):
    reserve[start_sentence] = dest_sentence


def del_reserve(start_sentence):
    del reserve[start_sentence]


class _Translator:
    def __init__(self, start_language):
        load_reserve()
        self._start = start_language
        self._dest = 'ko'
        self._googletrans = translator.GoogleTranslator(self._start, self._dest)
        self._papagotrans = translator.PapagoTranslator(self._start, self._dest)

        self._engine = 'google'
        self._pronounce_engine = translator.NonePronunciation(self._start)

    def set_google(self):
        self._engine = 'google'

    def set_papago(self):
        self._engine = 'papago'

    def set_none_engine(self):
        self._engine = None

    def set_start_languaage(self, start_language):
        self._start = start_language

    def translate(self, sentence):
        if self._engine is None:
            return '', self._pronounce_engine.pronunciation(sentence)
        elif sentence in reserve:
            return reserve[sentence], ''
        elif self._engine == 'google':
            return self._googletrans.translate(sentence), self._pronounce_engine.pronunciation(sentence)
        elif self._engine == 'papago':
            return self._papagotrans.translate(sentence), self._pronounce_engine.pronunciation(sentence)

    def set_pronunciation_mode(self, option: bool):
        if option:
            self._pronounce_engine = translator.GooglePronunciation(self._start)
        else:
            self._pronounce_engine = translator.NonePronunciation(self._start)


class HandledLine:
    def __init__(self, is_translated, has_pronounce, origin_line, origin_pronounce, translated_line):
        self.origin_line, self.origin_pronounce, self.translated_line = origin_line, origin_pronounce, translated_line
        self._is_translated = is_translated
        self._has_pronounce = has_pronounce

    def valid_pronounce(self):
        return self._has_pronounce

    def is_translated(self):
        return self._is_translated


class LineHandler:
    split_tok = [
        '【', '】', '「', '」', '◇', '★'
    ]
    special_escape_letter = [
        'V', 'N', 'P', 'G', 'C', 'I'
    ]

    class _Split(Enum):
        NORMAL = 0
        ESCAPE_SEQUENCE = 1
        ESCAPE_SPECIAL_CASE = 2
        SENTENCE = 3
        INDENT = 4

    def _mode_set(self):
        if 'G' in self.mode:
            self.translator.set_google()
        elif 'P' in self.mode:
            self.translator.set_papago()
        elif 'X' in self.mode:
            self.translator.set_none_engine()
        if 'B' in self.mode:
            self.translator.set_pronunciation_mode(True)
        else:
            self.translator.set_pronunciation_mode(False)

    def __init__(self, start_language, mode="GN"):
        self.translator = _Translator(start_language=start_language)
        self.mode = mode.upper()
        self._mode_set()
        self._refresh_inner_variable()
        self._line = ''

    def _refresh_inner_variable(self):
        self.translated_split_line = []
        self.pronounce_list = []
        self.translated_sentence_count = 0

    def line(self, line, mode=None) -> HandledLine:
        if mode is not None:
            self.mode = mode.upper()
            self._mode_set()
        self._refresh_inner_variable()
        self._line = line
        self._line_split()
        return HandledLine(
            is_translated=self._is_translated(),
            has_pronounce='B' in self.mode and self._is_translated(),
            origin_line=line,
            origin_pronounce=self._get_pronounce(),
            translated_line=self._get_translated_line()
        )

    def _line_split(self):
        start_idx = 0
        i = 0
        status = self._Split.INDENT

        while i < len(self._line):
            if status == self._Split.INDENT:
                if self._line[i] == '　' or self._line[i] == ' ':
                    self.translated_split_line.append(self._line[i])
                else:
                    if self._line[i] in self.split_tok:
                        self.translated_split_line.append(self._line[i])
                        status = self._Split.NORMAL
                    elif self._line[i] == '\\':
                        start_idx = i
                        status = self._Split.ESCAPE_SEQUENCE
                    else:  # sentence start
                        start_idx = i
                        status = self._Split.SENTENCE
            elif status == self._Split.NORMAL:
                if self._line[i] in self.split_tok:
                    self.translated_split_line.append(self._line[i])
                elif self._line[i] == '\\':
                    start_idx = i
                    status = self._Split.ESCAPE_SEQUENCE
                else:  # sentence start
                    start_idx = i
                    status = self._Split.SENTENCE
            elif status == self._Split.ESCAPE_SEQUENCE:  # \\ 인식
                if self._line[i].upper() in self.special_escape_letter:
                    status = self._Split.ESCAPE_SPECIAL_CASE
                else:
                    self.translated_split_line.append(self._line[start_idx:i + 1])
                    status = self._Split.NORMAL
            elif status == self._Split.ESCAPE_SPECIAL_CASE:
                if self._line[i] == ']':
                    self.translated_split_line.append(self._line[start_idx:(i + 1)])
                    status = self._Split.NORMAL
                else:
                    pass
            elif status == self._Split.SENTENCE:  # 문장
                if self._line[i] in self.split_tok:
                    sentence = self._line[start_idx:i]
                    result = self.translator.translate(sentence)
                    self.translated_split_line.append(result[0])
                    self.pronounce_list.append(result[1])
                    self.translated_sentence_count += 1
                    self.translated_split_line.append(self._line[i])
                    status = self._Split.NORMAL
                elif self._line[i] == '\\':
                    sentence = self._line[start_idx:i]
                    result = self.translator.translate(sentence)
                    self.translated_split_line.append(result[0])
                    self.pronounce_list.append(result[1])
                    self.translated_sentence_count += 1
                    start_idx = i
                    status = self._Split.ESCAPE_SEQUENCE
                else:
                    pass
            i += 1
        if status == self._Split.SENTENCE:
            sentence = self._line[start_idx:i]
            result = self.translator.translate(sentence)
            self.translated_split_line.append(result[0])
            self.pronounce_list.append(result[1])
            self.translated_sentence_count += 1
        elif status == self._Split.ESCAPE_SEQUENCE or status == self._Split.ESCAPE_SPECIAL_CASE:
            self.translated_split_line.append(self._line[start_idx:i])
        elif status == self._Split.INDENT:
            self.translated_split_line.append(self._line[:])

    def _is_translated(self):
        return (not ('X' in self.mode)) and self.translated_sentence_count > 0

    def _get_translated_line(self):
        return ''.join(self.translated_split_line)

    def _get_pronounce(self):
        return ' '.join(self.pronounce_list)


def line_count(text, newline='LF'):
    if newline.upper() == 'LF':
        newline = '\n'
    elif newline.upper() == 'CR':
        newline = '\r'
    cnt = text.count(newline) + 1
    return cnt


if __name__ == '__main__':
    text = r'''\C[4]フロスティア\C[0]「あなたたちがハメルダー？」'''
    l = LineHandler('ja', mode='GB')
    res = l.line(text)
    print("origin: " + res.origin_line)

    print("trans:", res.is_translated())

    print("res:", res.translated_line)
    print("발음:", res.origin_pronounce)
    pass
