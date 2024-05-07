import numpy as np
from numpy import array
from pyope.ope import OPE, ValueRange

# 读入处理txt文件,返回二维数组，明文和密文
def LoadTxtMethod(filename):
    cipher = OPE(b'long key' * 2, in_range=ValueRange(0, 10000000),
                 out_range=ValueRange(0, 100000000))
    result_m = list()  # 明文点
    result_c = []
    for line in open(filename):  # 逐行打开文档.
        plain_text = line.split(' ', 1)
        plain_text[0] = float(plain_text[0])
        plain_text[1] = float(plain_text[1])
        plain_text_arr = np.array(plain_text)  # 转化数据格式
        result_m.append(plain_text_arr)  # 把数据添加到result序列中
        cipher_text = []
        cipher_text.append(cipher.encrypt(int(plain_text[0] * 1000000)))
        cipher_text.append(cipher.encrypt(int(plain_text[1] * 1000000)))
        cipher_text_arr = np.array(cipher_text)  # 转化数据格式
        result_c.append(cipher_text_arr)
        print("加密" + str(cipher_text_arr[0]) + ',' + str(cipher_text_arr[1]))
    return array(result_c)


def WriteTxt(cipher_txt):
    with open('NE_encrypt.txt', 'a', encoding='utf-8') as f:
        for x in cipher_txt:
            print(type(x))
            strings = str(x[0]) + ' ' + str(x[1]) + '\n'
            f.write(strings)


if __name__ == "__main__":
    data = LoadTxtMethod('NE.txt')  # 调用上面数据处理程序
    WriteTxt(data)  # 加密之后的数据存放于cipherText.txt中
