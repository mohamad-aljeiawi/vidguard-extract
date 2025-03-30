import re
import six
import json


def decode(text: str, alt: bool = False) -> str:
    text: str = re.sub(r"\s+|/\*.*?\*/", "", six.ensure_str(text))
    if alt:
        data: str = text.split("+(ﾟɆﾟ)[ﾟoﾟ]")[1]
        chars: list[str] = data.split("+(ﾟɆﾟ)[ﾟεﾟ]+")[1:]
        char1: str = "ღ"
        char2: str = "(ﾟɆﾟ)[ﾟΘﾟ]"
    else:
        data: str = text.split("+(ﾟДﾟ)[ﾟoﾟ]")[1]
        chars: list[str] = data.split("+(ﾟДﾟ)[ﾟεﾟ]+")[1:]
        char1: str = "c"
        char2: str = "(ﾟДﾟ)['0']"

    txt: str = ""
    for char in chars:
        char: str = (
            char.replace("(oﾟｰﾟo)", "u")
            .replace(char1, "0")
            .replace(char2, "c")
            .replace("ﾟΘﾟ", "1")
            .replace("!+[]", "1")
            .replace("-~", "1+")
            .replace("o", "3")
            .replace("_", "3")
            .replace("ﾟｰﾟ", "4")
            .replace("(+", "(")
        )
        char: str = re.sub(r"\((\d)\)", r"\1", char)

        c: str = ""
        subchar: str = ""
        for v in char:
            c += v
            try:
                x: str = c
                subchar += str(eval(x))
                c = ""
            except:
                pass
        if subchar != "":
            txt += subchar + "|"
    txt: str = txt[:-1].replace("+", "")

    txt_result: str = "".join([chr(int(n, 8)) for n in txt.split("|")])

    return toStringCases(txt_result)


def toStringCases(txt_result: str) -> str:
    sum_base: str = ""
    m3: bool = False
    if ".toString(" in txt_result:
        if "+(" in txt_result:
            m3 = True
            try:
                sum_base = "+" + re.search(
                    r".toString...(\d+).", txt_result, re.DOTALL
                ).groups(1)
            except:
                sum_base = ""
            txt_pre_temp: list[tuple[str, str]] = re.findall(
                r"..(\d),(\d+).", txt_result, re.DOTALL
            )
            txt_temp: list[tuple[str, str]] = [(n, b) for b, n in txt_pre_temp]
        else:
            txt_temp: list[tuple[str, str]] = re.findall(
                r"(\d+)\.0.\w+.([^\)]+).", txt_result, re.DOTALL
            )
        for numero, base in txt_temp:
            code: str = toString(int(numero), eval(base + sum_base))
            if m3:
                txt_result: str = re.sub(
                    r'"|\+',
                    "",
                    txt_result.replace("(" + base + "," + numero + ")", code),
                )
            else:
                txt_result: str = re.sub(
                    r"'|\+",
                    "",
                    txt_result.replace(numero + ".0.toString(" + base + ")", code),
                )
    return txt_result


def toString(number: int, base: int) -> str:
    string: str = "0123456789abcdefghijklmnopqrstuvwxyz"
    if number < base:
        return string[number]
    else:
        return toString(number // base, base) + string[number % base]


def extract_json(text: str) -> dict | None:
    json_pattern: re.Pattern = re.compile(r"[a-zA-Z0-9_.]+\s*=\s*(\{.*\})", re.DOTALL)
    match: re.Match | None = json_pattern.search(text)

    if match:
        json_str: str = match.group(1)
        try:
            json_str: str = json_str.replace('\\"', '"')
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    try:
        start: int = text.find("{")
        end: int = text.rfind("}") + 1

        if start >= 0 and end > start:
            potential_json: str = text[start:end]
            return json.loads(potential_json)
    except json.JSONDecodeError:
        pass

    return None
