import time

import requests
import googletrans


class Translator:
    def __init__(self, src_lang, dst_lang):
        self.src_lang = src_lang
        self.dst_lang = dst_lang

    def set_language(self, src_lang, dst_lang):
        self.src_lang = src_lang
        self.dst_lang = dst_lang

    def translate(self, text):
        return text


class PapagoTranslator(Translator):
    client_data=[
        ("9vhtpYd3rRj4EdOitIoy", "T36JZ7v8wG"),
        ("jk6oH5dM4BTToeshgUkx", "ofLogrsELk"),
        ("6NPoXmujOsoijG5x8YCk", "0b3YJXgn0G"),
        ("v96pK5PZzK7QiDEyY5kj", "hUsVkkf9xN"),
        ("M0iUyXFR_sw6D51SqdsC", "8a4B2rBZcw"),
        ("VTt0hxfMz1irOlOrXtZn", "b67pQ4bvx9"),
        ("mVjwR0ImGdDgaFqaboCb", "ZuExN6SE4A")
    ]

    url = "https://openapi.naver.com/v1/papago/n2mt"

    def change_client(self):
        if self.try_changing_cnt < len(self.client_data):
            self.client_idx = (self.client_idx + 1) % len(self.client_data)
            self.header={"X-Naver-Client-Id": self.client_data[self.client_idx][0],
                         "X-Naver-Client-Secret": self.client_data[self.client_idx][1]}
            self.try_changing_cnt += 1
            return True
        else:
            return False

    def _get_translate(self, data):
        try:
            response = requests.post(self.url, headers=self.header, data=data)
            rescode = response.status_code
            if (rescode == 200):
                send_data = response.json()
                trans_data = (send_data['message']['result']['translatedText'])
                self.try_changing_cnt=0
                return trans_data
            else:
                if self.change_client():
                    time.sleep(0.3 * (self.try_changing_cnt + 1))
                    return self._get_translate(data)
                else:
                    raise Exception("Papago translator error")
        except:
            if self.try_changing_cnt < len(self.client_data):
                self.try_changing_cnt += 1
                time.sleep(0.3 * (self.try_changing_cnt + 1))
                return self._get_translate(data)
            else:
                raise Exception("Papago translator error")

    def __init__(self, src_lang, dst_lang):
        self.client_idx=0
        self.try_changing_cnt=0
        self.header = {"X-Naver-Client-Id": self.client_data[self.client_idx][0],
                       "X-Naver-Client-Secret": self.client_data[self.client_idx][1]}
        super().__init__(src_lang, dst_lang)

    def set_language(self, src_lang, dst_lang):
        super().set_language(src_lang, dst_lang)

    def translate(self, text):
        data = {'text': text,
                'source': self.src_lang,
                'target': self.dst_lang}
        return self._get_translate(data)



class GoogleTranslator(Translator):
    def __init__(self, src_lang, dst_lang):
        self.trans = googletrans.Translator()
        self.fail_count = 0
        super().__init__(src_lang, dst_lang)

    def set_language(self, src_lang, dst_lang):
        super().set_language(src_lang, dst_lang)

    def translate(self, text):
        while True:
            try:
                self.cur = self.trans.translate(text, dest=self.dst_lang, src=self.src_lang)
            except:
                if self.fail_count < 10:
                    time.sleep(0.3 * (1.43 ** self.fail_count))
                    self.fail_count += 1
                    continue
                else:
                    raise Exception("google translator exception")
            else:
                self.fail_count = 0
                break
        return self.cur.text

    def cur_pronunciation(self):
        return self.cur.pronunciation


class _Pronunciation:
    def __init__(self, lang):
        self.lang = lang

    def pronunciation(self, text):
        return ''


class GooglePronunciation(_Pronunciation):
    def __init__(self, lang):
        super().__init__(lang)
        self.engine = googletrans.Translator()

    def pronunciation(self, text):
        return self.engine.translate(text, dest=self.lang).pronunciation


class NonePronunciation(_Pronunciation):
    def __init__(self, lang):
        super().__init__(lang)

    def pronunciation(self, text):
        return ''


if __name__ == '__main__':
    text = "桧山すみれ"
    sr = 'ja'
    dst = 'ko'
    tr = [PapagoTranslator(sr, dst), GoogleTranslator(sr, dst)]
    print(PapagoTranslator(sr, dst).translate(text))
