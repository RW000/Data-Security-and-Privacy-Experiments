# __author: Junebao
# data:2020/3/9

from bitarray import bitarray


class MyDES:
    def __init__(self):
        self.child_keys = []

    @staticmethod
    def _bit_encode(s: str) -> str:
        """
        将字符串转换为01字符串的形式
        """
        return bitarray(
            ''.join([bin(int('1' + hex(c)[2:], 16))[3:]
                     for c in s.encode('utf-8')])).to01()

    def _str_to__fixed_len_bit(self, s: str, length: int) -> str:
        """
        将字符串转变为固定长度的01字符串
        :param s: 要转换的字符串
        :param length: 目标长度
        :return: 长度为length的01字符串
        """
        bit_iv = self._bit_encode(s)
        while len(bit_iv) < length:
            bit_iv += '0'
        return bit_iv[: length]


    @staticmethod
    def _bit_decode(s: list):
        return ''.join([chr(i) for i in [int(b, 2) for b in s]])

    @staticmethod
    def _negate(s: str):
        result = ""
        try:
            for i in s:
                result += '0' if i == '1' else '1'
            return result
        except:
            print("密钥错误")
            raise

    @staticmethod
    def _replace_block(block: str, replace_table: tuple) -> str:
        """
        对单个块进行置换
        Args:
            block: str, 要进行转换的64位长的01字符串
            replace_table: 转换表
        Return:
            返回转换后的字符串
        """
        result = ""
        for i in replace_table:
            try:
                result += block[i - 1]
            except IndexError:
                print(i)
                # print(f"block= {block}, len={len(block)}")
                raise
        return result

    def _processing_encode_input(self, enter: str) -> list:
        """
        将输入的字符串转换为二进制形式，并没64位为一组进行分割
        """
        result = []
        bit_string = self._bit_encode(enter)
        # 如果长度不能被64整除，就补零
        if len(bit_string) % 64 != 0:
            for i in range(64 - len(bit_string) % 64):
                bit_string += '0'
        for i in range(len(bit_string) // 64):
            result.append(bit_string[i * 64: i * 64 + 64])
        # print(f"转换为二进制后的初始明文： {result}")
        return result

    @staticmethod
    def _processing_decode_input(enter: str) -> list:
        result = []
        try:
            input_list = enter.split("0x")[1:]
            int_list = [int("0x" + i, 16) for i in input_list]
            for i in int_list:
                bin_data = str(bin(i))[2:]
                while len(bin_data) < 64:
                    bin_data = '0' + bin_data
                result.append(bin_data)
            return result
        except Exception as e:
            raise

    def _key_conversion(self, key: str):
        """
        将64位原始密钥转换为56位的密钥，并进行一次置换
        """
        key = self._bit_encode(key)
        while len(key) < 64:
            key += '0'
        first_key = key[:64]
        key_replace_table = (
            57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18,
            10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36,
            63, 55, 47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22,
            14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4
        )
        return self._replace_block(first_key, key_replace_table)

    def _spin_key(self, key: str):
        """
        旋转获得子密钥
        """
        kc = self._key_conversion(key)
        first, second = kc[0: 28], kc[28: 56]
        spin_table = (1, 2, 4, 6, 8, 10, 12, 14, 15, 17, 19, 21, 23, 25, 27, 28)
        for i in range(1, 17):
            first_after_spin = first[spin_table[i - 1]:] + first[:spin_table[i - 1]]
            second_after_spin = second[spin_table[i - 1]:] + second[:spin_table[i - 1]]
            # print(f"旋转后的key： left: {first_after_spin}, right: {second_after_spin}")
            yield first_after_spin + second_after_spin

    def _key_selection_replacement(self, key: str):
        """
        通过选择置换得到48位的子密钥
        """
        # 先置空
        self.child_keys = []
        key_select_table = (
            14, 17, 11, 24, 1, 5, 3, 28, 15, 6, 21, 10,
            23, 19, 12, 4, 26, 8, 16, 7, 27, 20, 13, 2,
            41, 52, 31, 37, 47, 55, 30, 40, 51, 45, 33, 48,
            44, 49, 39, 56, 34, 53, 46, 42, 50, 36, 29, 32
        )
        for child_key56 in self._spin_key(key):
            self.child_keys.append(self._replace_block(child_key56, key_select_table))

    def _init_replace_block(self, block: str):
        """
        对一个块进行初态置换
        """
        replace_table = (
            58, 50, 42, 34, 26, 18, 10, 2,
            60, 52, 44, 36, 28, 20, 12, 4,
            62, 54, 46, 38, 30, 22, 14, 6,
            64, 56, 48, 40, 32, 24, 16, 8,
            57, 49, 41, 33, 25, 17, 9, 1,
            59, 51, 43, 35, 27, 19, 11, 3,
            61, 53, 45, 37, 29, 21, 13, 5,
            63, 55, 47, 39, 31, 23, 15, 7
        )
        return self._replace_block(block, replace_table)

    def _end_replace_block(self, block: str) -> str:
        """
        对某一个块进行终态转换
        """
        replace_table = (
            40, 8, 48, 16, 56, 24, 64, 32,
            39, 7, 47, 15, 55, 23, 63, 31,
            38, 6, 46, 14, 54, 22, 62, 30,
            37, 5, 45, 13, 53, 21, 61, 29,
            36, 4, 44, 12, 52, 20, 60, 28,
            35, 3, 43, 11, 51, 19, 59, 27,
            34, 2, 42, 10, 50, 18, 58, 26,
            33, 1, 41, 9, 49, 17, 57, 25
        )
        return self._replace_block(block, replace_table)

    @staticmethod
    def _block_extend(block: str) -> str:
        """
        拓展置换
        """
        extended_block = ""
        extend_table = (
            32, 1, 2, 3, 4, 5,
            4, 5, 6, 7, 8, 9,
            8, 9, 10, 11, 12, 13,
            12, 13, 14, 15, 16, 17,
            16, 17, 18, 19, 20, 21,
            20, 21, 22, 23, 24, 25,
            24, 25, 26, 27, 28, 29,
            28, 29, 30, 31, 32, 1
        )
        for i in extend_table:
            extended_block += block[i - 1]
        return extended_block

    @staticmethod
    def _not_or(a: str, b: str) -> str:
        """
        对两个01字符串做异或
        """
        result = ""
        size = len(a) if len(a) < len(a) else len(b)
        for i in range(size):
            result += '0' if a[i] == b[i] else '1'
        return result

    def _s_box_replace(self, block48: str) -> str:
        """
        S盒置换，将48位的输入转换为32位输出
        """
        s_box_table = (
            (
                (14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7),
                (0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8),
                (4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0),
                (15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13),
            ),
            (
                (15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10),
                (3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5),
                (0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15),
                (13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9),
            ),
            (
                (10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8),
                (13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1),
                (13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7),
                (1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12),
            ),
            (
                (7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15),
                (13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9),
                (10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4),
                (3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14),
            ),
            (
                (2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9),
                (14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6),
                (4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14),
                (11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3),
            ),
            (
                (12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11),
                (10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8),
                (9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6),
                (4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13),
            ),
            (
                (4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1),
                (13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6),
                (1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2),
                (6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12),
            ),
            (
                (13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7),
                (1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2),
                (7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8),
                (2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11),
            )
        )
        result = ""
        for i in range(8):
            row_bit = (block48[i * 6] + block48[i * 6 + 5]).encode("utf-8")
            line_bit = (block48[i * 6 + 1: i * 6 + 5]).encode("utf-8")
            row = int(row_bit, 2)
            line = int(line_bit, 2)
            # print(f"第{row}行， 第{line}列")
            data = s_box_table[i][row][line]
            no_full = str(bin(data))[2:]
            while len(no_full) < 4:
                no_full = '0' + no_full
            result += no_full
        return result

    def _s_box_compression(self, num: int, block48: str) -> str:
        """
        对经过拓展置换后的48位01串进行S盒压缩，有两部：
          1. 与key做异或
          2. 根据S盒压缩表经48位压缩为36位
        Args:
            num: 第几次迭代
            block48: right
        Return:
            返回经过S盒压缩后的32位01字符串
        """
        result_not_or = self._not_or(block48, self.child_keys[num])
        # print(f"与key 做异或后的结果{result_not_or}")
        return self._s_box_replace(result_not_or)

    def _p_box_replacement(self, block32: str) -> str:
        """
        P盒置换
        Return:
            返回经过P盒置换后的32位01串
        """
        p_box_replace_table = (
            16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31, 10,
            2, 8, 24, 14, 32, 27, 3, 9, 19, 13, 30, 6, 22, 11, 4, 25,
        )
        return self._replace_block(block32, p_box_replace_table)

    def _f_function(self, right: str, is_decode: bool, num: int):
        right = self._block_extend(right)
        if is_decode:
            sbc_result = self._s_box_compression(15 - num, right)
        else:
            sbc_result = self._s_box_compression(num, right)
        # print(f"s盒压缩后的结果:{sbc_result}")
        return self._p_box_replacement(sbc_result)

    def _iteration(self, block: str, key: str, is_decode: bool) -> str:
        self._key_selection_replacement(key)
        for i in range(16):
            left, right = block[0: 32], block[32: 64]
            next_left = right
            f_result = self._f_function(right, is_decode, i)
            right = self._not_or(left, f_result)
            block = next_left + right
        return block[32:] + block[:32]


    def encode_by_cbc(self, enter: str, des_key: str, iv: str):
        """
        使用 CBC 模式进行 DES加密
        :param enter: 明文
        :param des_key: 密钥
        :param iv: CBC模式中的因子
        :return: 加密后的十六进制格式密文串
        """
        bit_iv = self._str_to__fixed_len_bit(iv, 64)
        result = ""
        blocks = self._processing_encode_input(enter)
        previous = bit_iv
        for block in blocks:
            block = self._not_or(block, previous)
            irb_result = self._init_replace_block(block)
            block_result = self._iteration(irb_result, des_key, is_decode=False)
            block_result = self._end_replace_block(block_result)
            previous = block_result
            result += str(hex(int(block_result.encode(), 2)))
        return result


    def decode_by_cbc(self, cipher_text: str, des_key: str, iv: str):
        bit_iv = self._str_to__fixed_len_bit(iv, 64)
        result = []
        blocks = self._processing_decode_input(cipher_text)
        previous = bit_iv
        for block in blocks:
            irb_result = self._init_replace_block(block)
            block_result = self._iteration(irb_result, des_key, is_decode=True)
            block_result = self._end_replace_block(block_result)
            block_result = self._not_or(block_result, previous)
            previous = block
            for i in range(0, len(block_result), 8):
                result.append(block_result[i: i+8])
        return self._bit_decode(result)


if __name__ == '__main__':
    key = "hahahha"
    iv = "this is iv"
    md = MyDES()
    cbc_encode = md.encode_by_cbc('http://blog.junebao.top', des_key=key, iv=iv)
    print(f"CBC mode encryption： {cbc_encode}")
    print(f"CBC mode decrypt： {md.decode_by_cbc(cbc_encode, des_key=key, iv=iv)}")


