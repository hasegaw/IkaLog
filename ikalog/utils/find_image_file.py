import os

from ikalog.utils.ikautils import IkaUtils
from ikalog.utils.localization import Localization

def find_image_file(img_file=None, languages=None):
    print('find_image_file: img_file %s languages %s' % (img_file, languages))
    if languages is None:
        languages = Localization.get_game_languages()

    if languages is not None:
        if not isinstance(languages, list):
            languages = [lang]

        for lang in languages:
            f = IkaUtils.get_path('masks', lang, img_file)
            if os.path.exists(f):
                return f

    f = IkaUtils.get_path('masks', img_file)
    if os.path.exists(f):
        return f

    f = IkaUtils.get_path(img_file)
    if os.path.exists(f):
        return f

    f = IkaUtils.get_path('masks', 'ja', img_file)
    if os.path.exists(f):
        IkaUtils.dprint('%s: mask %s: using ja version' %
            (self, img_file))
        return f

    raise Exception('Could not find image file %s (lang %s)' % (img_file, lang))

