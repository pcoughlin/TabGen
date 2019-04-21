from adsk.core import Application

from .parameter import Parameter

from ..util import automaticWidthId
from ..util import userDefinedWidthId


app = Application.get()
ui = app.userInterface


def clean_param(param):
    return param.replace(' ', '_').replace('(', '').replace(')', '').lower()


class Parameters:

    def __init__(self, parent, name, vertical, tab_params, xdir, ydir):
        self._parent = parent

        dirname = ydir if vertical else xdir
        self._clean_name = clean_param(name)
        self.prefix = '{}_{}'.format(self._clean_name,
                                     dirname)

        self.x, self.y, self.z = (False, False, False)

        if (xdir == 'x' or ydir == 'x'):
            self.x = True
        if (xdir == 'y' or ydir == 'y'):
            self.y = True
        if (xdir == 'z' or ydir == 'z'):
            self.z = True

        self._pdfingerw = Parameter(parent.face.name,
                                    'dfingerw',
                                    abs(round(tab_params.default_width, 5)),
                                    favorite=True)
        self._xlength = Parameter(name,
                                  '{}_length'.format(xdir),
                                  abs(round(parent.x_length, 5)),
                                  favorite=True)
        self._ylength = Parameter(name,
                                  '{}_length'.format(ydir),
                                  abs(round(parent.y_length, 5)),
                                  favorite=True)
        self._dfingerw = Parameter(self.prefix,
                                   'dfingerw',
                                   '{}_dfingerw'.format(self._clean_name))
        self._fingerd = Parameter(self.prefix,
                                  'fingerd',
                                  -round(tab_params.depth, 5),
                                  favorite=True)

        self.create_params(tab_params)

    def create_params(self, tab_params):
        funcs = {
            automaticWidthId: self.create_auto_params,
            userDefinedWidthId: self.create_defined_params
        }
        func = funcs[tab_params.finger_type]
        func(tab_params)

    def create_auto_params(self, tab_params):
        self.fingers = Parameter(self.prefix,
                                 'fingers',
                                 'max(3; (ceil(floor({0}_length/{0}_dfingerw)/2)*2)-1)',
                                 units='')
        self.fingerw = Parameter(self.prefix,
                                 'fingerw',
                                 '{0}_length / {0}_fingers')
        self.foffset = Parameter(self.prefix,
                                 'foffset',
                                 '{0}_fingerw')
        self.notches = Parameter(self.prefix,
                                 'notches',
                                 'floor({0}_fingers/2)',
                                 units='')
        self.extrude_count = Parameter(self.prefix,
                                       'extrude_count',
                                       '{0}_notches',
                                       units='')
        self.fdistance = Parameter(self.prefix,
                                   'fdistance',
                                   '({0}_fingers - 3)*{0}_fingerw')

    def create_defined_params(self, tab_params):
        self.fingers = Parameter(self.prefix,
                                 'fingers',
                                 'floor({0}_length / {0}_dfingerw)',
                                 units='')
        self.fingerw = Parameter(self.prefix,
                                 'fingerw',
                                 '{0}_dfingerw')
        self.notches = Parameter(self.prefix,
                                 'notches',
                                 'floor({0}_length / (2 * {0}_fingerw))',
                                 units='')
        self.notch_length = Parameter(self.prefix,
                                      'notch_length',
                                      '2 * {0}_fingerw * {0}_notches')
        self.foffset = Parameter(self.prefix,
                                 'foffset',
                                 '({0}_length - {0}_notch_length + {0}_fingerw)/2')
        self.extrude_count = Parameter(self.prefix,
                                       'extrude_count',
                                       '{0}_notches - 1',
                                       units='')
        self.fdistance = Parameter(self.prefix,
                                   'fdistance',
                                   '{0}_length - {0}_foffset*2 - {0}_fingerw')

    def add_far_length(self, expression, units='cm'):
        self.far_length = Parameter(self._clean_name,
                                    '{}_length'.format(self._alternate_axis),
                                    abs(expression),
                                    units=units,
                                    favorite=True)

        if expression < 0:
            self.far_distance = Parameter(self._clean_name,
                                          '{}_distance'.format(self._alternate_axis),
                                          '-{}'.format(self.far_length.name),
                                          units=units)
            fingerdstr = 'abs({})'.format(self.fingerd.name) if self.fingerd.value < 0 else self.fingerd.name
            d2expr = '-(abs({}) - {})'.format(self.far_length.name, fingerdstr)
        else:
            self.far_distance = self.far_length
            fingerdstr = 'abs({})'.format(self.fingerd.name) if self.fingerd.value < 0 else self.fingerd.name
            d2expr = '{} - {}'.format(self.far_length.name, fingerdstr)

        self.distance_two = Parameter(self._clean_name,
                                      '{}_distance2'.format(self._alternate_axis),
                                      d2expr)

    @property
    def _alternate_axis(self):
        if not self.x:
            return 'x'
        if not self.y:
            return 'y'
        if not self.z:
            return 'z'

    @property
    def name(self):
        return self._parent.name

    @property
    def xlength(self):
        return self._xlength

    @property
    def ylength(self):
        return self._ylength

    @property
    def fingerd(self):
        return self._fingerd

    @property
    def dfingerw(self):
        return self._dfingerw