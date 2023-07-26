import datetime
import encodings

from enum import Enum, unique

from src.main.configs.SystemConfigs import PATH_FILE_LOG
from src.main.utils.CommonUtils import CommonUtil


@unique
class NoticeEnum(Enum):
    """
        All kinds of error messages for everywhere
    """

    APPLICATION_CONFIG_ERROR    = {"CODE": "9999", "TYPE": "ERROR", "MSG": "Read application_*.yaml failed: [%s]"}
    READ_FILE_ERROR             = {"CODE": "9998", "TYPE": "ERROR", "MSG": "Read file failed: [%s]"}
    ARGUMENT_ERROR              = {"CODE": "9997", "TYPE": "ERROR", "MSG": "Argument is incorrect. argument = [%s]"}

    NETWORK_CONNECTED           = {"CODE": "01",   "TYPE": "INFO",  "MSG": "Connected to socket server"}
    SEND_MSG_TO_SERVER          = {"CODE": "02",   "TYPE": "INFO",  "MSG": "Sending msg to server: midNo = [%s], msg = [%s]"}
    SEND_MSG_FAILED             = {"CODE": "03",   "TYPE": "ERROR", "MSG": "Send message to socket failed: [%s], msg = [%s]"}
    NETWORK_DISCONNECTED        = {"CODE": "04",   "TYPE": "INFO",  "MSG": "Disconnected to socket server"}
    RECONNECT_TOO_MANY_TIMES    = {"CODE": "05",   "TYPE": "ERROR", "MSG": "Reconnected too many times"}

    CONNECT_FAILED              = {"CODE": "11",   "TYPE": "ERROR", "MSG": "Connect failed: [%s]"}
    CONNECTION_ALREADY_CLOSED   = {"CODE": "110",  "TYPE": "WARN",  "MSG": "Connection already closed"}
    CONNECT_TIME_OUT            = {"CODE": "12",   "TYPE": "ERROR", "MSG": "Connect timed out: timed out after %ds"}
    THREAD_LOOP_ERROR           = {"CODE": "13",   "TYPE": "ERROR", "MSG": "Thread loop exception: %s"}

    INITIALIZATION_FAILED       = {"CODE": "20",   "TYPE": "ERROR", "MSG": "Initializing thread variables failed: [%s]"}

    DECODE_MSG_FAILED           = {"CODE": "30",   "TYPE": "ERROR", "MSG": "Decode main-thread message failed: [%s], msg = [%s]"}

    READ_MSG_FAILED             = {"CODE": "51",   "TYPE": "ERROR", "MSG": "Reading message from socket failed: [%s]"}
    READ_MSG_EMPTY              = {"CODE": "52",   "TYPE": "ERROR", "MSG": "Getting empty message from socket, msg = [%s]"}

    CONVERSION_FAILED           = {"CODE": "60",   "TYPE": "ERROR", "MSG": "Converting protocol data failed, type = [%s], log = [%s], value = [%s]"}


    # static method for everywhere
    @staticmethod
    def Print_Msg(cls, self, *args):
        # cls(class) cannot be None, otherwise we can't trace the source
        CommonUtil.CheckNone(cls, "Argument [cls] cannot be None")

        # fill all the args into msg
        msg = self.value["MSG"] % args

        # format error messageX
        msg = "[%s: %s - %s] Message code = %s, msg = %s" %\
              (
                  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                  self.value["TYPE"],
                  cls.__class__,
                  self.value["CODE"],
                  msg
              )

        # print the msg
        print(msg)

        # return message in case it would be used somewhere
        return msg


    @staticmethod
    def Log(cls, self, *args):
        # cls(class) cannot be None, otherwise we can't trace the source
        CommonUtil.CheckNone(cls, "Argument [cls] cannot be None")

        # get complete message and print it
        msg = NoticeEnum.Print_Msg(cls, self, *args)

        # write the message into local(or remote) log file(s)
        if PATH_FILE_LOG is not None and len(PATH_FILE_LOG) > 0:
            for each in PATH_FILE_LOG:
                log_file = open(
                    each + datetime.datetime.now().strftime('%Y-%m') + u'.log',
                    'a+',
                    encoding = encodings.utf_8.getregentry().name
                )
                log_file.write(msg + "\n")
                log_file.close()

