import logging.handlers
import socket
import ssl


class SSLSysLogHandler(logging.handlers.SysLogHandler):

    # We need to paste all this in because __init__ bitches otherwise
    # This all comes from logging.handlers.SysLogHandler

    LOG_EMERG = 0  # system is unusable
    LOG_ALERT = 1  # action must be taken immediately
    LOG_CRIT = 2  # critical conditions
    LOG_ERR = 3  # error conditions
    LOG_WARNING = 4  # warning conditions
    LOG_NOTICE = 5  # normal but significant condition
    LOG_INFO = 6  # informational
    LOG_DEBUG = 7  # debug-level messages

    #  facility codes
    LOG_KERN = 0  # kernel messages
    LOG_USER = 1  # random user-level messages
    LOG_MAIL = 2  # mail system
    LOG_DAEMON = 3  # system daemons
    LOG_AUTH = 4  # security/authorization messages
    LOG_SYSLOG = 5  # messages generated internally by syslogd
    LOG_LPR = 6  # line printer subsystem
    LOG_NEWS = 7  # network news subsystem
    LOG_UUCP = 8  # UUCP subsystem
    LOG_CRON = 9  # clock daemon
    LOG_AUTHPRIV = 10  # security/authorization messages (private)
    LOG_FTP = 11  # FTP daemon

    #  other codes through 15 reserved for system use
    LOG_LOCAL0 = 16  # reserved for local use
    LOG_LOCAL1 = 17  # reserved for local use
    LOG_LOCAL2 = 18  # reserved for local use
    LOG_LOCAL3 = 19  # reserved for local use
    LOG_LOCAL4 = 20  # reserved for local use
    LOG_LOCAL5 = 21  # reserved for local use
    LOG_LOCAL6 = 22  # reserved for local use
    LOG_LOCAL7 = 23  # reserved for local use

    priority_names = {
        "alert": LOG_ALERT,
        "crit": LOG_CRIT,
        "critical": LOG_CRIT,
        "debug": LOG_DEBUG,
        "emerg": LOG_EMERG,
        "err": LOG_ERR,
        "error": LOG_ERR,  # DEPRECATED
        "info": LOG_INFO,
        "notice": LOG_NOTICE,
        "panic": LOG_EMERG,  # DEPRECATED
        "warn": LOG_WARNING,  # DEPRECATED
        "warning": LOG_WARNING,
    }

    facility_names = {
        "auth": LOG_AUTH,
        "authpriv": LOG_AUTHPRIV,
        "cron": LOG_CRON,
        "daemon": LOG_DAEMON,
        "ftp": LOG_FTP,
        "kern": LOG_KERN,
        "lpr": LOG_LPR,
        "mail": LOG_MAIL,
        "news": LOG_NEWS,
        "security": LOG_AUTH,  # DEPRECATED
        "syslog": LOG_SYSLOG,
        "user": LOG_USER,
        "uucp": LOG_UUCP,
        "local0": LOG_LOCAL0,
        "local1": LOG_LOCAL1,
        "local2": LOG_LOCAL2,
        "local3": LOG_LOCAL3,
        "local4": LOG_LOCAL4,
        "local5": LOG_LOCAL5,
        "local6": LOG_LOCAL6,
        "local7": LOG_LOCAL7,
    }

    # The map below appears to be trivially lowercasing the key. However,
    # there's more to it than meets the eye - in some locales, lowercasing
    # gives unexpected results. See SF #1524081: in the Turkish locale,
    # "INFO".lower() != "info"
    priority_map = {
        "DEBUG": "debug",
        "INFO": "info",
        "WARNING": "warning",
        "ERROR": "error",
        "CRITICAL": "critical",
    }

    def __init__(self, address, certs=None, facility=LOG_USER):
        logging.Handler.__init__(self)
        self.address = address
        self.facility = facility
        self.unixsocket = False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if certs:
            self.socket = ssl.wrap_socket(
                s, ca_certs=certs, cert_reqs=ssl.CERT_REQUIRED
            )
        else:
            self.socket = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)
        self.socket.connect(address)

    def close(self):
        self.socket.close()
        logging.Handler.close(self)

    def emit(self, record):
        msg = bytes("{}\n".format(self.format(record)))
        try:
            self.socket.write(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)
