# -*- coding: utf-8 -*-
"""
**Engine**

"""
# import inspect
import os
# import sys
import datetime
import importlib

import yaml


try:
    # IHEClassInitError, IHEStringError, IHETypeError, IHEKeyError, IHEFileError
    from .exception import IHEClassInitError
except ImportError:
    from IHEWAengine.exception import IHEClassInitError


class Base(object):
    """This Base class

    Load base.yml file.

    Args:
        product (str): Product name of data products.
        is_print (bool): Is to print status message.
    """
    def __init__(self):
        """Class instantiation
        """
        pass

    def _scan_templates(self):
        pass


class Engine(Base):
    """Engine class

    After initialise the class, data downloading will automatically start.

    Args:
        workspace (str): Directory to config.yml.
        config (str): Configuration yaml file name.
        kwargs (dict): Other arguments.
    """
    def __init__(self, workspace='', config='', **kwargs):
        """Class instantiation
        """
        self.must_keys = {
            'engines': [],
            # 'template': ['provider', 'name'],
            # 'page': ['header', 'footer'],
            # 'content': ['cover', 'title', 'section']
        }

        self.__status = {
            'messages': {
                0: 'S: WA.Engine {f:>20} : status {c}, {m}',
                1: 'E: WA.Engine {f:>20} : status {c}: {m}',
                2: 'W: WA.Engine {f:>20} : status {c}: {m}',
            },
            'code': 0,
            'message': '',
            'is_print': True
        }
        self.__conf = {
            'workspace': '',
            'path': '',
            'name': '',
            'time': {
                'start': None,
                'now': None,
                'end': None
            },
            'data': {
                # 'engines': {},
            },
            'folder': {
                'engine1': {
                    'tmp': '',
                    'res': '',
                    'fig': ''
                },
                'engine2': {
                    'tmp': '',
                    'res': '',
                    'fig': ''
                }
            },
            'log': {
                'engine1': {
                    'fname': 'log.{name}.txt',
                    'file': '{path}/log.txt',
                    'fp': None,
                    'status': -1,  # -1: not found, 0: closed, 1: opened
                },
                'engine2': {
                    'fname': 'log.{name}.txt',
                    'file': '{path}/log.txt',
                    'fp': None,
                    'status': -1,  # -1: not found, 0: closed, 1: opened
                }
            }
        }
        self.__eng = {
            'engine1': {
                'name': '',
                'module': None
            },
            'engine2': {
                'name': '',
                'module': None
            }
        }

        if isinstance(workspace, str):
            path = os.path.join(workspace, 'IHEWAengine')
            if not os.path.exists(path):
                os.makedirs(path)
            self.__conf['workspace'] = workspace
            self.__conf['path'] = path
        else:
            self.__status['code'] = 1

        if isinstance(config, str):
            self.__conf['name'] = config
        else:
            self.__status['code'] = 1

        if self.__status['code'] == 0:
            self.__status['code'] = self._time()
            if self.__status['code'] != 0:
                print('_time', self.__status['code'])

            self.__status['code'] = self._conf()
            if self.__status['code'] != 0:
                print('_conf', self.__status['code'])

        if self.__status['code'] == 0:
            self.__status['code'] = self._engine()
            if self.__status['code'] != 0:
                print('_engine', self.__status['code'])

        # Class Engine
        if self.__status['code'] == 0:
            self._engine_prepare()

            self._engine_init()
            self._engine_start()
            self._engine_finish()

            self.__status['message'] = ''
        else:
            raise IHEClassInitError('Engine') from None

    def _engine_prepare(self) -> int:
        """
        Returns:
            int: Status.
        """
        self._folder()
        self._log()

        return

    def _engine_init(self) -> int:
        """
        Returns:
            int: Status.
        """
        status = -1
        for engine_key, engine_val in self.__eng.items():
            if self.__eng[engine_key]['module'] is not None:
                # print(self.__eng[engine_key]['name'])
                engine = self.__eng[engine_key]['module'].Engine(self.__conf)
                status = 0
            else:
                status = 1
                self.__status['code'] = status

        return status

    def _engine_start(self) -> int:
        """
        Returns:
            int: Status.
        """
        status = -1
        # self.__tmp['module'].DownloadData(self.__status, self.__conf)
        # self.__tmp['module'].download()
        # self.__tmp['module'].convert()
        # self.__tmp['module'].saveas()
        # self.__tmp['module'].clean()

        status = 0
        return status

    def _engine_finish(self) -> int:
        """
        Returns:
            int: Status.
        """
        status = -1
        # self._log_close()
        # self._folder_clean()

        status = 0
        return status

    def _conf(self) -> int:
        status_code = 0
        data = None

        file_conf = os.path.join(self.__conf['workspace'], self.__conf['name'])
        with open(file_conf) as fp:
            data = yaml.load(fp, Loader=yaml.FullLoader)

        if data is not None:
            for key in self.must_keys.keys():
                status_code += self._conf_keys(key, data)
                # status_code += self._conf_keys('template', data)
                # status_code += self._conf_keys('page', data)
                # status_code += self._conf_keys('content', data)
        else:
            status_code = 1

        if status_code == 0:
            self.__conf['data'] = data

        return status_code

    def _conf_keys(self, key, data) -> int:
        status_code = 0
        try:
            if isinstance(data[key], dict):
               data_keys = data[key].keys()
            else:
                raise KeyError
        except KeyError:
            status_code = 1
        else:
            for data_key in self.must_keys[key]:
                if data_key not in data_keys:
                    status_code += 1

        return status_code

    def _time(self) -> int:
        """

        Returns:
            int: Status.
        """
        status_code = -1
        now = datetime.datetime.now()

        self.__conf['time']['start'] = now
        self.__conf['time']['now'] = now
        self.__conf['time']['end'] = now
        status_code = 0

        return status_code

    def _folder(self) -> dict:
        folder = {}

        # Define folder
        for engine_key, engine_val in self.__eng.items():
            path = self.__conf['path']
            engine_name = engine_val['name']

            path = os.path.join(path, engine_name)
            # folder[engine_key] = {
            #     'tmp': os.path.join(path, 'temporary'),
            #     'res': os.path.join(path, 'result'),
            #     'fig': os.path.join(path, 'figure')
            # }
            folder[engine_key] = {
                'res': path
            }

            for key, value in folder[engine_key].items():
                if not os.path.exists(value):
                    os.makedirs(value)

        self.__conf['folder'] = folder
        # print(self.__conf['folder'])

        return folder

    def _folder_clean(self):
        statue = 1

        # shutil

        # re = glob.glob(os.path.join(folder['r'], '*'))
        # for f in re:
        #     os.remove(os.path.join(folder['r'], f))

        # for r, d, f in os.walk(path):
        #     for file in f:
        #         if '.txt' in file:
        #             files.append(os.path.join(r, file))

        return statue

    def _log(self) -> dict:
        """
        Returns:
            dict: log.
        """
        # Class self.__conf['log']
        status = -1
        log = {}

        for engine_key, engine_val in self.__eng.items():
            if self.__status['code'] == 0:
                path = self.__conf['path']
                engine_name = engine_val['name']

                # time = self.__conf['time']['start']
                # time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f')

                fname = self.__conf['log'][engine_key]['fname'].format(name=engine_name)
                file = os.path.join(path, fname)

                # -1: not found, 0: closed, 1: opened
                fp = self._log_create(file)

                log[engine_key] = {}
                log[engine_key]['fname'] = fname
                log[engine_key]['file'] = file
                log[engine_key]['fp'] = fp
                log[engine_key]['status'] = status

        self.__conf['log'] = log

        return log

    def _log_create(self, file):
        time = datetime.datetime.now()
        time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.__conf['time']['now'] = time

        print('Create log file "{f}"'.format(f=file))
        txt = '{t}: IHEWAengine'.format(t=time_str)

        fp = open(file, 'w+')
        fp.write('{}\n'.format(txt))
        # for key, value in self.__conf['product'].items():
        #     if key != 'data':
        #         fp.write('{:>26s}: {}\n'.format(key, str(value)))

        return fp

    def _engine(self) -> int:
        """

        Returns:
            dict: engine.
        """
        status_code = -1
        engines = self.__eng
        for engine_key, engine_val in self.__conf['data']['engines'].items():
            module_name = engines[engine_key]['name']
            module_obj = engines[engine_key]['module']

            if self.__conf['data']['engines'] is None:
                print('Please select an engine!')

                status_code = 0
            else:
                try:
                    module_provider = engine_key
                    module_template = self.__conf['data']['engines'][engine_key]['name']
                except KeyError:
                    status_code = 1
                else:
                    module_name_base = '{tmp}.{nam}'.format(
                        tmp=module_provider,
                        nam=module_template)

                    # Load module
                    # module_obj = None
                    if module_obj is None:
                        is_reload_module = False
                    else:
                        if module_name == module_name_base:
                            is_reload_module = True
                        else:
                            is_reload_module = False
                    engines[engine_key]['name'] = module_name_base
                    # print(engines[engine_key])

                    if is_reload_module:
                        try:
                            module_obj = importlib.reload(module_obj)
                        except ImportError:
                            status_code = 1
                        else:
                            engines[engine_key]['module'] = module_obj
                            print('Reloaded module.{nam}'.format(
                                nam=engines[engine_key]['name']))
                            status_code = 0
                    else:
                        try:
                            # importlib.import_module('.FAO',
                            #                         '.templates.IHE')
                            #
                            # importlib.import_module('templates.IHE.FAO')

                            # importlib.import_module('IHEWAengine.templates.IHE.FAO')
                            module_obj = \
                                importlib.import_module('.{n}'.format(n=module_template),
                                                        '.{p}'.format(p=module_provider))
                            print('Loaded module from .{nam}'.format(
                                nam=engines[engine_key]['name']))
                        except ImportError:
                            module_obj = \
                                importlib.import_module('IHEWAengine.{nam}'.format(
                                    nam=engines[engine_key]['name']))
                            print('Loaded module from IHEWAengine.{nam}'.format(
                                nam=engines[engine_key]['name']))
                            status_code = 1
                        finally:
                            if module_obj is not None:
                                engines[engine_key]['module'] = module_obj
                                status_code = 0
                            else:
                                status_code = 1

        # print(engines)
        self.__eng = {}
        for engine_key, engine_val in engines.items():
            module_name = engines[engine_key]['name']
            module_obj = engines[engine_key]['module']

            if module_obj is not None:
                self.__eng[engine_key] = engines[engine_key]

        return status_code

    @staticmethod
    def get_config(self):
        print(self.__conf)


if __name__ == "__main__":
    print('\nEngine\n=====')
    # path = os.path.join(
    #     os.getcwd(),
    #     os.path.dirname(
    #         inspect.getfile(
    #             inspect.currentframe())),
    #     '../', '../', 'tests'
    # )
    #
    # engine = Engine(path, 'test_engine.yml')

    # engine.get_config()
    # print(engine._Engine__conf['path'], '\n',
    #       engine._Engine__conf['name'], '\n',
    #       engine._Engine__conf['time'], '\n',
    #       engine._Engine__conf['data'])
