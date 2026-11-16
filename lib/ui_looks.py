# -*- coding: utf-8 -*-
# ********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# UI looks: the colour presets zynthian-sys ships in config/ui-looks, one
# file per look setting the sixteen ZYNTHIAN_UI_COLOR_* and the font.
# The preset the UI page shows is derived from the current settings (the
# look they all match, else Custom); choosing another one fills the fields.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
# ********************************************************************

import os
import re

LOOK_KEYS = [
    'ZYNTHIAN_UI_COLOR_BG', 'ZYNTHIAN_UI_COLOR_TX', 'ZYNTHIAN_UI_COLOR_TX_OFF', 'ZYNTHIAN_UI_COLOR_ON',
    'ZYNTHIAN_UI_COLOR_OFF', 'ZYNTHIAN_UI_COLOR_LOW_ON', 'ZYNTHIAN_UI_COLOR_HL', 'ZYNTHIAN_UI_COLOR_ML',
    'ZYNTHIAN_UI_COLOR_PANEL_BG', 'ZYNTHIAN_UI_COLOR_PANEL_HL', 'ZYNTHIAN_UI_COLOR_INFO', 'ZYNTHIAN_UI_COLOR_MIDI',
    'ZYNTHIAN_UI_COLOR_ALT', 'ZYNTHIAN_UI_COLOR_ALT2', 'ZYNTHIAN_UI_COLOR_ERROR', 'ZYNTHIAN_UI_COLOR_WARN',
    'ZYNTHIAN_UI_FONT_FAMILY',
]

PRESET_FIELD = '_UI_COLOR_PRESET'
CUSTOM_LABEL = 'Custom (the colours below)'

_EXPORT = re.compile(r'^export ([A-Z0-9_]+)="([^"]*)"$')
_TITLE = re.compile(r'^# ([^:]+)')


def looks_dir(sys_dir=None):
    return os.path.join(sys_dir or os.environ.get('ZYNTHIAN_SYS_DIR', '/zynthian/zynthian-sys'), 'config', 'ui-looks')


def read_looks(sys_dir=None):
    """{name: {'title', 'values'}} for every look file that sets all seventeen keys."""
    looks = {}
    d = looks_dir(sys_dir)
    try:
        names = sorted(f for f in os.listdir(d) if f.endswith('.sh'))
    except OSError:
        return looks
    for fname in names:
        title = None
        values = {}
        with open(os.path.join(d, fname)) as f:
            for line in f:
                line = line.rstrip('\n')
                if title is None:
                    m = _TITLE.match(line)
                    title = m.group(1).strip() if m else fname[:-3]
                m = _EXPORT.match(line)
                if m:
                    values[m.group(1)] = m.group(2)
        if all(k in values for k in LOOK_KEYS):
            looks[fname[:-3]] = {'title': title, 'values': {k: values[k] for k in LOOK_KEYS}}
    return looks


def current_preset(looks, current):
    """The look every current value matches, else '' (Custom)."""
    for name, look in looks.items():
        if all(current.get(k) == v for k, v in look['values'].items()):
            return name
    return ''


def preset_field(looks, current):
    """The UI page's select: Custom, then each look by its title."""
    options = [''] + sorted(looks)
    labels = {'': CUSTOM_LABEL}
    labels.update({name: look['title'] for name, look in looks.items()})
    return {
        'type': 'select',
        'title': 'Colour preset',
        'value': current_preset(looks, current),
        'options': options,
        'option_labels': labels,
    }


def apply_preset(looks, chosen, current, arguments):
    """When `chosen` is a look other than the one the current settings match, put its seventeen values in
    the posted arguments; otherwise leave the fields as they were posted."""
    if chosen not in looks or chosen == current_preset(looks, current):
        return
    for k, v in looks[chosen]['values'].items():
        arguments[k] = [v]
