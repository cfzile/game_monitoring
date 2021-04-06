SITE_MONITORING_CSS_V_34_NAME = 'Мониторинг серверов CS:S v34'
SITE_SIGN_IN_NAME = 'Вход'
SITE_SIGN_UP_NAME = 'Регистрация'
SITE_SERVER_ADD_NAME = 'Добавить сервер'
NON_CORRECT_DATA = 'Введены некорректные данные'
SITE_FAQ_NAME = 'FAQ'
SITE_BUY_PLACE_NAME = 'Купить место'
EVENT_INFO = "Инфо."
EVENT_ERROR = "Ошибка"
DATE_FORMAT_JS = 'mm/dd/yy'
DATE_FORMAT_PYTHON = '%m/%d/%Y'
DATE_FORMAT_PYTHON_TO = 'm/d/Y'
PRICE_OF_PREMIUM_PLACE = 3
NUM_SERVERS_ON_PAGE = 100

def SUCH_SERVER_EXIST(addr=''):
    return 'Сервер с адресом %s уже добавлен' % addr

def NON_CORRECT_DATA_OR_SERVER_DONT_RUN(ip, port):
    return NON_CORRECT_DATA + (" %s:%s" % (ip, str(port))) + " или сервер не запущен"


administrator_email = 'administrator@gamemonitoring.site'
administrator_email_password = 'pasadministrator'
