import os


LOG_FILE = '{}/nginx.log'.format(os.path.dirname(os.path.abspath(__file__)))
TMP_FILE = '{}/es.position'.format(os.path.dirname(os.path.abspath(__file__)))


class LogParser:
    def __init__(self, filename, pos_file):
        self.log_file = filename
        self.pos_file = pos_file
        self.run()

    def run(self):
        pos, line = self.get_start_pos_n_line()
        print(pos)
        print(line)
        self.read_nginx_log(pos, line)
        self.write_cur_pos_n_line(10, 'bbb')

    def get_start_pos_n_line(self):
        """
        checks pos_file existence
        read values
        :return: (int start_position, str last_line)
        """
        if not os.path.isfile(self.pos_file):
            return 0, ''
        with open(self.pos_file) as f:
            pos = int(f.readline().strip())
            line = f.readline().strip()
            return pos, line

    def read_nginx_log(self, start_pos, last_line):
        """
        checks that file is valid and get new data
        :param start_pos: int, start position in log file
        :param last_line: str, last line value
        :return: None
        """
        if not os.path.isfile(self.log_file):
            return
        with open(self.log_file, 'r') as log_file:
            log_file.seek(start_pos, 0)
            if log_file.readline().strip() != last_line:
                raise 'File have been changed'

            time_from = last_line.split('\t')[2].split(':')
            line = log_file.readline().strip()
            while line:
                parts = line.strip().split('\t')
                params = {}
                for pair in parts:
                    key, value = pair.split(':')
                    params[key] = value

    def write_cur_pos_n_line(self, pos, line):
        with open(self.pos_file, 'w') as f:
            f.write('{}\n{}\n'.format(str(pos), line))

if __name__ == '__main__':
    LogParser(LOG_FILE, TMP_FILE)
