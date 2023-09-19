from StringTools import str_to_date, str_to_number
import PyPDF2


def clearmotion_entry(s):
    return None
    # splt = s.split()
    # for i in splt:
    #     print('uhhhh')


class Paycheck:
    def __init__(self, path=None, institution=None, process=True):
        self.path = path
        self.institution = institution
        self.result = 'Incomplete'

        self.rawdata = None
        self.summary = {}
        self.deductions = None
        if process:
            self.process()

    def process(self):
        try:
            self.get_rawdata()
            self.get_summary()
            self.get_deductions()
            self.result = 'Success'
        except Exception as e:
            print(f'File Extraction Failed: {self.path} {e}')
            self.result = 'Failed'

    def get_rawdata(self):
        pages_text = ''
        reader = PyPDF2.PdfReader(self.path, strict=False)
        for page in reader.pages:
            page_text = page.extract_text()
            pages_text = pages_text + page_text
        self.rawdata = pages_text

    def get_summary(self, debug=False):
        if debug:
            print(self.rawdata)
        self.summary = {'Starting Balance': None,
                        'Ending Balance': None,
                        'Starting Date': None,
                        'Ending Date': None}

    def get_deductions(self, debug=False):
        if debug:
            print(self.rawdata)
        self.deductions = None


class IRobotPaycheck(Paycheck):
    def __init__(self, path=None, institution='iRobot', process=True):
        super().__init__(path=path, institution=institution, process=process)


class ClearMotionPaycheck(Paycheck):
    def __init__(self, path=None, institution='ClearMotion', process=True):
        super().__init__(path=path, institution=institution, process=process)

    def get_summary(self, debug=False):
        lst = self.rawdata.split('\n')
        state = 0
        last_key = ''

        if debug:
            print(lst)

        keywords = {
            'Pay Period:': 1,
            'Earnings': 2
        }

        for item in lst:
            item = item.strip()

            for key in keywords.keys():
                if key in item:
                    last_key = key
                    state = keywords[key]

            if state == 0:
                pass
            elif state == 1:
                splt = item.replace(last_key, '').split('-')
                d1 = str_to_date(splt[0].strip())
                d2 = str_to_date(splt[-1].strip())
                if d1 is not None:
                    self.summary['Starting Date'] = d1[0]
                if d2 is not None:
                    self.summary['Ending Date'] = d2[0]
                state = 0
            elif state == 2:
                splt = item.split()
                if len(splt) > 4:
                    n = str_to_number(splt[2])
                    if n is not None:
                        self.summary['Earnings'] = n
                state = 0

    def get_deductions(self, debug=False):
        yr_rng = [self.summary['Starting Date'].year, self.summary['Ending Date'].year]
        state = 0
        last_state = 0
        lst = self.rawdata.split('\n')

        if debug:
            print(lst)

        keywords = {
            'Hours/Units Rate Amount Hours/Units Amount': 1,
        }

        for item in lst:
            item = item.strip()

            for key in keywords.keys():
                if key in item:
                    state = keywords[key]

            if state == 0:
                pass
            elif state == 1:
                entry = clearmotion_entry(item)
                if entry is not None:
                    print(entry)
