import os
import sys
import imp
import time
import threading
from six import exec_
import base64 as base
from types import ModuleType

class CORE():

    VERSION = 'v.0.2.16.4-st'

    import logging

    logging.basicConfig(
        level=logging.INFO,
        format=f'SMD_CORE %(asctime)s [ %(levelname)-2s ] (%(name)s) %(message)s'
    )
    _stream_handler = logging.StreamHandler()
    _stream_handler.setLevel(logging.INFO)
    __logger = logging.getLogger("CORE")
    info = lambda data: CORE.__logger.info(data)
    error = lambda data: CORE.__logger.error(data)

    class core_handler_comp(object):

        def __init__(self):

            self.__data__kn_, self.__data__nd_ = (7, 3, 55), 128
            self.__out = lambda __data__: "".join(map(self.__enc_sng_chr, __data__))
            self.__in = lambda __data__: "".join(map(self.__dec_sng_chr, __data__))
            self.decomposer = lambda __data__: self.__out(str(base.b64encode(str(__data__).encode('utf-8'))))
            self.composer = lambda __data__: base.b64decode(str(self.__in(__data__)[2:-1])).decode('utf-8')

        def __enc_sng_chr(self, _s_c):
            __data__k1_,__data__k2_,__data__k3_ = self.__data__kn_
            return chr((__data__k1_ * ord(_s_c) + __data__k2_) % self.__data__nd_)

        def __dec_sng_chr(self, _s_c):
            __data__k1_,__data__k2_,__data__k3_ = self.__data__kn_
            return chr(__data__k3_ * (ord(_s_c) - __data__k2_) % self.__data__nd_)


    class core_filesystem_manager(object):

        @staticmethod
        def include(_file_name):

            __module_name = None
            __module_name_is_not_free = True
            __module_name_iter = 0

            while __module_name_is_not_free:

                _name = f'.__s_{"0" if __module_name_iter < 10 else ""}{str(__module_name_iter)}_core_enc_p.smdc'
                if not os.path.exists(_name):
                    __module_name_is_not_free = False
                    __module_name = _name
                else:__module_name_iter+=1

            with open(_file_name, 'r') as data:

                __module_n_ = str(__module_name).split('.')[1]
                __raw_file_data = f"__SMD_CORE_MODULE_NAME__='{__module_n_}'\n{data.read()}"
                __raw_file_data = __raw_file_data.replace("logging.getLogger()",f"logging.getLogger('{__module_n_}')")
                __temp_core_handler_comp_obj = CORE.core_handler_comp()
                __module_data_raw = __temp_core_handler_comp_obj.decomposer(__raw_file_data)
                del __temp_core_handler_comp_obj

                with open(__module_name, 'w') as module:

                    module.write(__module_data_raw)


        @staticmethod
        def include_cf(_file_name):
            __module_data_raw = 'NDI='
            with open(_file_name, 'r') as __raw_file_data:
                __temp_core_handler_comp_obj = CORE.core_handler_comp()
                __raw_file_data__ = __raw_file_data.read()
                __module_data_raw = __temp_core_handler_comp_obj.decomposer(__raw_file_data__)
                __raw_file_data.close()
                del __temp_core_handler_comp_obj
                del __raw_file_data
                with open(_file_name, 'w') as __raw_file_data:
                    __raw_file_data.write(__module_data_raw)


        @staticmethod
        def init(_module_name):

            with open(_module_name, 'r') as data:

                __temp_core_handler_comp_obj = CORE.core_handler_comp()
                __module = __temp_core_handler_comp_obj.composer(data.read())
                del __temp_core_handler_comp_obj

                return __module


    def calculate(_function_):
        def wrapper(*args):
            __start_time__ = time.time()
            __result__ = _function_(*args)
            __end_time__ = time.time()
            CORE.info(f'{_function_.__name__} executed in {round((__end_time__-__start_time__)*1000.0,2)} ms.')
            return __result__
        return wrapper


    @staticmethod
    @calculate
    def __get_all():
        modules = []
        for module in os.listdir(f'{os.getcwd()}/kernel/smdc'):
            modules.append(f"{os.getcwd()}/kernel/smdc/{module}") if str(module).find('.smdc') > -1 else False
        return modules


    @staticmethod
    def __init_module(module):

        __module__ = imp.new_module(module)
        exec_(CORE.core_filesystem_manager.init(module), __module__.__dict__)

        return __module__


    @staticmethod
    @calculate
    def init():

        CORE.__logger.info(f'INIT SMD CORE ({CORE.VERSION})')
        __modules_raw = CORE.__get_all()
        __modules_raw.sort()

        for module in __modules_raw:

            CORE.__logger.info(f'Including module [{module}]')
            __module = CORE.__init_module(module)
            setattr(CORE, __module.__SMD_CORE_MODULE_NAME__, __module)
            CORE.__logger.info(f'Module [{module}] included as {__module.__SMD_CORE_MODULE_NAME__}')

            del __module

        del __modules_raw

        CORE.__logger.info('INIT SMD CORE DONE')


    @staticmethod
    @calculate
    def get_all_included_modules():

        __included_modules = []
        [__included_modules.append(_) if "core_enc" in _ else False for _ in CORE.__dict__]
        return __included_modules


    @staticmethod
    @calculate
    def execute(_class_,_function_,args):

        def __value_handler__(_func_,_args_,_storage_):
            try:
                return _storage_.append(_func_(_args_))
            except Exception as e:
                CORE.error(e)
                return _storage_.append([])

        __modules__ = CORE.get_all_included_modules()
        __processes__, __results, executed = [], [], False

        for _module_ in __modules__:
            _temp_module_obj = CORE.__dict__[_module_].__dict__[_class_]()
            _process = threading.Thread(
                target=__value_handler__,
                args=(getattr(_temp_module_obj,_function_),args,__results))
            __processes__.append(_process)
            _process.start()

        while not executed:
            executed = True
            if any(_.isAlive() for _ in __processes__):
                time.sleep(0.001)
            else:
                executed = False
                break

        for _ in __processes__:
            _.join()

        return __results
