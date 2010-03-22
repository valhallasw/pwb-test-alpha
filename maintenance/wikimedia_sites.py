"""
This script checks the language list of each Wikimedia multiple-language site
against the language lists
"""
#
# (C) Pywikipedia bot team, 2008-2010
#
# Distributed under the terms of the MIT license.
#

import sys, re

sys.path.append('..')
import wikipedia
import codecs

families = ['wikipedia', 'wiktionary', 'wikiquote', 'wikisource', 'wikibooks', 'wikinews', 'wikiversity']
familiesDict = {
    'wikipedia':  'wikipedias_wiki.php',
    'wiktionary': 'wiktionaries_wiki.php',
    'wikiquote':  'wikiquotes_wiki.php',
    'wikisource': 'wikisources_wiki.php',
    'wikibooks':  'wikibooks_wiki.php',
    'wikinews':   'wikinews_wiki.php',
    'wikiversity':'wikiversity_wiki.php',
}
exceptions = ['www']

def update_family():
    for family in families:
        wikipedia.output('Checking family %s:' % family)

        original = wikipedia.Family(family).languages_by_size
        obsolete = wikipedia.Family(family).obsolete

        url = 'http://s23.org/wikistats/%s' % familiesDict[family]
        uo = wikipedia.MyURLopener
        f = uo.open(url)
        text = f.read()

        if family == 'wikipedia':
            p = re.compile(r"\[\[:([a-z\-]{2,}):\|\1\]\].*?'''([0-9,]{1,})'''</span>\]", re.DOTALL)
        else:
            p = re.compile(r"\[http://([a-z\-]{2,}).%s.org/wiki/ \1].*?'''([0-9,]{1,})'''\]" % family, re.DOTALL)

        new = []
        for lang, cnt in p.findall(text):
            if lang in obsolete or lang in exceptions:
                # Ignore this language
                continue
            new.append(lang)
        if original == new:
            wikipedia.output(u'The lists match!')
        else:
            wikipedia.output(u"The lists don't match, the new list is:")
            text = u'        self.languages_by_size = [\r\n'
            line = '            '
            index = 0
            for lang in new:
                index += 1
                if index > 1:
                    line += u' '
                line += u"'%s'," % lang
                if index == 10:
                    text += u'%s\r\n' % line
                    line = '            '
                    index = 0
            if index > 0:
                text += u'%s\r\n' % line
            text += u'        ]'
            wikipedia.output(text)
            family_file_name = '../families/%s_family.py' % family
            family_file = codecs.open(family_file_name, 'r', 'utf8')
            old_text = family_text = family_file.read()
            old = re.findall(ur'(?msu)^ {8}self.languages_by_size.+?\]', family_text)[0]
            family_text = family_text.replace(old, text)
            family_file = codecs.open(family_file_name, 'w', 'utf8')
            family_file.write(family_text)
            family_file.close()

if __name__ == '__main__':
    try:
        update_family()
    finally:
        wikipedia.stopme()