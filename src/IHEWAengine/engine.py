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
            'code': 0
        }
        self.__conf = {
            'path': '',
            'name': '',
            'time': {
                'start': None,
                'now': None,
                'end': None
            },
            'data': {
                # 'engines': {},
                # # 'template': None,
                # # 'page': {},
                # # 'context': {}
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
            path = os.path.join(workspace)
            if not os.path.exists(path):
                os.makedirs(path)
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

        if self.__status['code'] == 0:
            for engine_key, engine_val in self.__eng.items():
                if self.__eng[engine_key]['module'] is not None:
                    # print(self.__eng[engine_key]['name'])
                    engine = self.__eng[engine_key]['module'].Engine(self.__conf)
                    # template.create()
                    # template.write()
                    # template.saveas()
                    # template.close()
                else:
                    # self.__status['code'] = 1
                    pass

        if self.__status['code'] != 0:
            print('Status', self.__status['code'])
            raise IHEClassInitError('Engine') from None

    def _conf(self) -> int:
        status_code = 0
        data = None

        file_conf = os.path.join(self.__conf['path'], self.__conf['name'])
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
                            print('Loaded module from .templates.{nam}'.format(
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
