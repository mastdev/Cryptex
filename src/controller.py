import argparse
import itertools
import sys
from typing import List

from vars import banner


class CLIManager:
    def __init__(self, cipher_list):
        self.cipher_list = cipher_list
        self.cipher_types = {}
        self.line = self.__add_extra("", 37, "-")

    def __add_extra(self, str, max, char):
        amount = max - len(str)
        if amount <= 0:
            str = str[: amount - 1]
            return str
        str = str + char * amount
        return str

    def print_ciphers(self):
        # loop over all the ciphers
        for name in self.cipher_list:
            # get the cipher type
            type = self.cipher_list[name].type
            # check if type is in dict, if not then add it
            if not type in self.cipher_types:
                self.cipher_types[type] = []
            # add cipher long name and short name to list of that ciphers type
            self.cipher_types[type].append([self.cipher_list[name].name, name])

        # print cryptex banner
        banner()

        # Printing magic
        for key in self.cipher_types:
            print("|" + self.__add_extra(f"-- {key}s", len(self.line), "-") + "|-- short name ------|")
            for item in self.cipher_types[key]:
                print("|      " + self.__add_extra(item[0], 30, " ") + f" |      {item[1]} \t   |")
        print("|" + self.line + "|" + self.__add_extra("", 20, "-") + "|")

    def print_output(self, output: str, args: argparse.Namespace):
        if "languages" in output:
            return

        if not output["success"]:
            sys.exit(f'Failed to run cipher "{args.cipher}"\nError: {output["text"]}')

        mode = ""
        if args.decode:
            mode = "Decode"
        elif args.encode:
            mode = "Encode"

        banner()

        if args.cipher == "pswd":
            print(
                f"""
        ------ Cipher: {args.cipher} -- Mode: {mode} ------
        Length   | {args.length}
        Password | {output['text']}
        ----
        """
            )
            return

        print(
            f"""
        ------ Cipher: {args.cipher} -- Mode: {mode} ------
        Input      | {args.text}
        Output     | {output['text']}

        Read File  | {args.input if args.input else "N/A"}
        Wrote File | {args.output if args.output else "N/A"}
        """
        )

        # remove output file from args for qr
        if args.cipher == "qr":
            args.output = None

        # if output then output
        if args.output:
            with open(args.output, "w") as f:
                f.write(f"{output['text']}")


class ArgumentParser:
    def __run(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()

        parser.add_argument("cipher", type=str, help="The cipher name", nargs="?")

        # Modes
        parser.add_argument("-e", "--encode", dest="encode", action="store_true", help="Encode mode")
        parser.add_argument("-d", "--decode", dest="decode", action="store_true", help="Decode mode")

        # Input
        parser.add_argument("-t", "--text", dest="text", type=str, help="The input text")
        parser.add_argument("-k", "--key", dest="key", type=str, help="The key")
        parser.add_argument("-ex", "--exclude", dest="exclude", type=str, help="The exclude list")
        parser.add_argument("-o", "--output", dest="output", type=str, help="output file")
        parser.add_argument("-i", "--input", dest="input", type=str, help="input file")
        parser.add_argument("-iw", "--imageWidth", dest="imageWidth", type=int, help="image width")
        parser.add_argument("-m", "--monocromatic", dest="monocromatic", action="store_true", help="monocromatic")
        parser.add_argument("-lang", dest="languages", action="store_true", help="show languages")
        parser.add_argument("-src", dest="src_lang", type=str, help="source language")
        parser.add_argument("-dest", dest="dest_lang", type=str, help="destination language")
        parser.add_argument("-len", dest="length", type=int, help="length")

        args = parser.parse_args()

        return args

    def parse_string(self, string: List[str]) -> argparse.Namespace:
        sys.argv = [" "] + string
        parsed_args = self.__run()
        return parsed_args


class Controller:
    def __init__(self, cipher_list):
        self.cipher_list = cipher_list
        self.parser = ArgumentParser()
        self.cli = CLIManager(self.cipher_list)

    def run(self):
        output = None

        try:
            first_text = sys.argv[sys.argv.index("-t") + 1]
            sys.argv[sys.argv.index("-t") + 1] = f'"{first_text}"'
        except ValueError:
            first_text = "N/A"

        layers = [[s.replace('"', '') for s in list(y)] for x, y in itertools.groupby(sys.argv[1:], lambda z: z == "+") if not x]

        for layer in layers:
            args = self.parser.parse_string(layer)

            if not args.cipher:
                sys.exit("No cipher selected.")

            try:
                if not args.cipher.lower() in self.cipher_list:
                    raise
                module = self.cipher_list[args.cipher]
            except:
                sys.exit(f'Cipher "{args.cipher}" may not exist')

            func = None

            if args.input:
                with open(args.input, "r") as f:
                    data = f.readlines()
                    data = "".join(data)
                    args.text = data

            if args.encode:
                func = module.encode
            elif args.decode:
                func = module.decode
            else:
                print("No mode selected. see the help menu for more info")
                module.print_options()
                sys.exit()

            if output:
                args.text = output["text"]

            output = func(args)

        args.text = first_text
        self.cli.print_output(output, args)
