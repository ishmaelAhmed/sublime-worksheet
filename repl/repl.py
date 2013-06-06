import pexpect
from ftfy import fix_text


class ReplResult():
    def __init__(self, text="", is_timeout=False, is_eof=False, is_last_line=False):
        if len(text.strip()) > 0 and not is_last_line:
            text += "\n"
        self.text = text
        self.is_timeout = is_timeout
        self.is_eof = is_eof

    def __str__(self):
        return self.text


class Repl():
    def __init__(self, cmd, prompt, prefix, timeout=10):
        self.prefix = prefix
        self.repl = pexpect.spawn(cmd)
        base_prompt = [pexpect.EOF, pexpect.TIMEOUT]
        self.prompt = base_prompt + self.repl.compile_pattern_list(prompt)
        self.repl.timeout = timeout
        self.repl.expect_list(self.prompt)

    def correspond(self, input, is_last_line=False):
        prefix = self.prefix
        if is_last_line:
            prefix = "\n" + prefix
            input += "\n"
        self.repl.send(input)
        index = self.repl.expect_list(self.prompt)
        if index == 0:
            # EOF
            return ReplResult(is_eof=True)
        elif index == 1:
            # Timeout
            return ReplResult(prefix + "Execution timed out.",
                is_timeout=True)
        else:
            # Regular prompt
            return ReplResult('\n'.join([
                prefix + line
                for line in fix_text(unicode(self.repl.before)).split("\n")
                if len(line.strip())
            ][1:]))

    def close(self):
        self.repl.close()
