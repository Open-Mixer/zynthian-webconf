# -*- coding: utf-8 -*-
# ********************************************************************
# The UI page's colour preset (lib/ui_looks.py): the looks zynthian-sys
# ships in config/ui-looks, the preset the current settings match, and a
# chosen preset filling the sixteen colours and the font.
#
#   python3 -m unittest discover -s tests
# ********************************************************************
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import ui_looks  # noqa: E402

KEYS = ui_looks.LOOK_KEYS

STOCK = dict(zip(KEYS, ['#000000', '#ffffff', '#e0e0e0', '#ff0000', '#5a626d', '#b00000', '#00c000', '#f0f000',
                        '#3a424d', '#2a323d', '#8080ff', '#19b1f7', '#ff00ff', '#ff9000', '#ff0000', '#ff9000',
                        'Audiowide']))
VINTAGE = dict(zip(KEYS, ['#0b0e11', '#eaf0f4', '#8a97a3', '#e8732c', '#0d1115', '#693d24', '#e9dfc6', '#f2b03a',
                          '#15191e', '#242b33', '#8a97a3', '#34d17b', '#34d17b', '#f2b632', '#ff5a4d', '#ffbf3d',
                          'Inter']))


def write_look(d, name, title, values):
    with open(os.path.join(d, name + '.sh'), 'w') as f:
        f.write('# %s: a look.\n# pin sha256:0 (ignored here)\n' % title)
        for k in KEYS:
            f.write('export %s="%s"\n' % (k, values[k]))


class UiLooksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = os.path.join(self.tmp.name, 'config', 'ui-looks')
        os.makedirs(self.dir)
        write_look(self.dir, 'stock', 'Stock', STOCK)
        write_look(self.dir, 'openmixer-vintage', 'OpenMixer vintage', VINTAGE)
        self.sys_dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_sixteen_colours_and_the_font(self):
        self.assertEqual(len(KEYS), 17)
        self.assertEqual(sum(k.startswith('ZYNTHIAN_UI_COLOR_') for k in KEYS), 16)
        self.assertEqual(KEYS[-1], 'ZYNTHIAN_UI_FONT_FAMILY')

    def test_looks_are_read_with_their_titles(self):
        looks = ui_looks.read_looks(self.sys_dir)
        self.assertEqual(sorted(looks), ['openmixer-vintage', 'stock'])
        self.assertEqual(looks['openmixer-vintage']['title'], 'OpenMixer vintage')
        self.assertEqual(looks['openmixer-vintage']['values'], VINTAGE)

    def test_no_looks_directory_offers_none(self):
        self.assertEqual(ui_looks.read_looks(os.path.join(self.tmp.name, 'nowhere')), {})

    def test_a_look_missing_a_key_is_left_out(self):
        with open(os.path.join(self.dir, 'broken.sh'), 'w') as f:
            f.write('# Broken\nexport ZYNTHIAN_UI_COLOR_BG="#000000"\n')
        self.assertNotIn('broken', ui_looks.read_looks(self.sys_dir))

    def test_the_current_preset_is_the_look_every_value_matches(self):
        looks = ui_looks.read_looks(self.sys_dir)
        self.assertEqual(ui_looks.current_preset(looks, dict(VINTAGE)), 'openmixer-vintage')
        self.assertEqual(ui_looks.current_preset(looks, dict(STOCK)), 'stock')
        changed = dict(VINTAGE, ZYNTHIAN_UI_COLOR_INFO='#123456')
        self.assertEqual(ui_looks.current_preset(looks, changed), '')

    def test_a_newly_chosen_preset_fills_the_seventeen(self):
        looks = ui_looks.read_looks(self.sys_dir)
        args = {k: [v] for k, v in STOCK.items()}
        args['ZYNTHIAN_UI_POWER_SAVE_MINUTES'] = ['60']
        ui_looks.apply_preset(looks, 'openmixer-vintage', STOCK, args)
        self.assertEqual({k: args[k][0] for k in KEYS}, VINTAGE)
        self.assertEqual(args['ZYNTHIAN_UI_POWER_SAVE_MINUTES'], ['60'])

    def test_an_unchanged_preset_keeps_the_fields_as_edited(self):
        looks = ui_looks.read_looks(self.sys_dir)
        args = {k: [v] for k, v in VINTAGE.items()}
        args['ZYNTHIAN_UI_COLOR_INFO'] = ['#123456']
        ui_looks.apply_preset(looks, 'openmixer-vintage', VINTAGE, args)
        self.assertEqual(args['ZYNTHIAN_UI_COLOR_INFO'], ['#123456'])

    def test_custom_or_unknown_changes_nothing(self):
        looks = ui_looks.read_looks(self.sys_dir)
        for chosen in ('', 'no-such-look'):
            args = {k: [v] for k, v in STOCK.items()}
            ui_looks.apply_preset(looks, chosen, VINTAGE, args)
            self.assertEqual({k: args[k][0] for k in KEYS}, STOCK)

    def test_the_select_lists_custom_then_each_look(self):
        looks = ui_looks.read_looks(self.sys_dir)
        field = ui_looks.preset_field(looks, dict(VINTAGE))
        self.assertEqual(field['type'], 'select')
        self.assertEqual(field['value'], 'openmixer-vintage')
        self.assertEqual(field['options'], ['', 'openmixer-vintage', 'stock'])
        self.assertEqual(field['option_labels'][''], 'Custom (the colours below)')
        self.assertEqual(field['option_labels']['stock'], 'Stock')


if __name__ == '__main__':
    unittest.main()
