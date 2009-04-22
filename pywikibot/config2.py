# -*- coding: utf-8 -*-
#
# (C) Rob W.W. Hooft, 2003
# (C) Pywikipedia bot team, 2003-2009
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'

import os, re
import sys as __sys

# IMPORTANT:
# Do not change any of the variables in this file. Instead, make
# a file user-config.py, and overwrite values in there.

# Note: all variables defined in this module are made available to bots as
# configuration settings, *except* variable names beginning with an
# underscore (example: _variable).  Be sure to use an underscore on any
# variables that are intended only for internal use and not to be exported
# to other modules.

############## ACCOUNT SETTINGS ##############

# The family of sites we are working on. wikipedia.py will import
# families/xxx_family.py so if you want to change this variable,
# you need to write such a file.
family = 'wikipedia'
# The language code of the site we're working on.
mylang = 'language'
# The default interface for communicating with the site
# currently the only defined interface is 'APISite', so don't change this!
site_interface = 'APISite'
# The dictionary usernames should contain a username for each site where you
# have a bot account. Please set your usernames by adding such lines to your
# user-config.py:
#
# usernames['wikipedia']['de'] = 'myGermanUsername'
# usernames['wiktionary']['en'] = 'myEnglishUsername'
#
# If you have a sysop account on some wikis, this will be used to delete pages
# or to edit locked pages if you add such lines to your
# user-config.py:
#
# sysopnames['wikipedia']['de'] = 'myGermanUsername'
# sysopnames['wiktionary']['en'] = 'myEnglishUsername'
usernames = {}
sysopnames = {}
disambiguation_comment = {}
gdab_namespaces = {}

# Solve captchas in the webbrowser. Setting this to False will result in the 
# exception CaptchaError be thrown if a captcha is encountered. 
solve_captcha = True

# Some sites will require password identication to access the HTML pages at
# the site. If you have any such site, add lines to your user-config.py of
# the following form:
#
# authenticate['en.wikipedia.org'] = ('John','XXXXX')
#
# where John is your login name, and XXXXX your password.
# Note:
# 1. This is only for sites that use authentication in the form that gives
#    you a popup for name and password when you try to access any data, NOT
#    for, for example, wiki usernames
# 2. You must use the hostname of the site, not its family/language pair
authenticate = {}

# password_file = ".passwd"
# A password file with default passwords. For more information, please
# see LoginManager.readPassword in login.py.
# By default you are asked for a password on the terminal.
password_file = None

# edit summary to use if not supplied by bot script
# WARNING: this should NEVER be used in practice, ALWAYS supply a more
#          relevant summary for bot edits
default_edit_summary = u'Wikipedia python library v.2'

# Get the names of all known families, and initialize
# with empty dictionaries
def _get_base_dir():
    """Return the directory in which user-specific information is stored.

    This is determined in the following order -
    1.  If the script was called with a -dir: argument, use the directory
        provided in this argument
    2.  If the user has a PYWIKIBOT2_DIR environment variable, use the value
        of it
    3.  Use (and if necessary create) a 'pywikibot' folder (Windows) or
        '.pywikibot' directory (Unix and similar) under the user's home
        directory.
    
    """
    NAME = "pywikibot"
    for arg in __sys.argv[1:]:
        if arg.startswith("-dir:"):
            base_dir = arg[5:]
            __sys.argv.remove(arg)
            break
    else:
        if "PYWIKIBOT2_DIR" in os.environ:
            base_dir = os.environ["PYWIKIBOT2_DIR"]
        else:
            is_windows = __sys.platform == 'win32' 
            home = os.path.expanduser("~") 
            if is_windows: 
                base_dir = os.path.join(home, "Application Data", NAME) 
            else: 
                base_dir = os.path.join(home, "."+NAME) 
            if not os.path.isdir(base_dir): 
                os.makedirs(base_dir, mode=0700) 
    if not os.path.isabs(base_dir):
        base_dir = os.path.normpath(os.path.join(os.getcwd(), base_dir))
    # make sure this path is valid and that it contains user-config file
    if not os.path.isdir(base_dir):
        raise RuntimeError("Directory '%(base_dir)s' does not exist."
                           % locals())
    if not os.path.exists(os.path.join(base_dir, "user-config.py")):
        raise RuntimeError("No user-config.py found in directory '%(base_dir)s'."
                           % locals())
    return base_dir

_base_dir = _get_base_dir()
# families/ is a subdirectory of the directory in which config.py is found
for _filename in os.listdir(
                    os.path.join(os.path.dirname(__file__), 'families')):
    if _filename.endswith("_family.py"):
        familyName = _filename[ : -len("_family.py")]
        usernames[familyName] = {}
        sysopnames[familyName] = {}
        disambiguation_comment[familyName] = {}

# Set to True to override the {{bots}} exclusion protocol (at your own risk!)
ignore_bot_templates = False

############## USER INTERFACE SETTINGS ##############

# The encoding that's used in the user's console, i.e. how strings are encoded
# when they are read by raw_input(). On Windows systems' DOS box, this should
# be 'cp850' ('cp437' for older versions). Linux users might try 'iso-8859-1'
# or 'utf-8'.
# This default code should work fine, so you don't have to think about it.
# TODO: consider getting rid of this config variable.
try:
    console_encoding = __sys.stdout.encoding
except:
    #When using pywikipedia inside a daemonized twisted application,
    #we get "StdioOnnaStick instance has no attribute 'encoding'"
    console_encoding = None

# The encoding in which textfiles are stored, which contain lists of page titles.
textfile_encoding = 'utf-8'

# tkinter isn't yet ready
userinterface = 'terminal'

# Should we transliterate characters that do not exist in the console
# character set?
# True: whenever possible
# False: never - always replace them by question marks
# Currently only works if interface 'terminal' is set.
transliterate = True

# Should the system bell be ringed if the bot expects user input?
ring_bell = False

# Colorization can be used to markup important text parts of the output.
# On Linux/Unix terminals, ANSI escape codes are used for this. On Windows,
# it is done by a DLL call via ctypes. ctypes is only available since
# Python 2.5, so if you're using Python 2.4 or lower on Windows, you should
# upgrade.
# Set this to False if you're using Linux and your tty doesn't support
# ANSI colors.
try:
    # Don't print colorized when the output is, for example, piped to a file.
    colorized_output = __sys.stdout.isatty()
except:
    colorized_output = False

############## EXTERNAL EDITOR SETTINGS ##############
# The command for the editor you want to use. If set to None, a simple Tkinter
# editor will be used.
# On Windows systems, this script tries to determine the default text editor.
if __sys.platform=='win32':
    try:
        import _winreg
        _key1 = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.txt\OpenWithProgids')
        _progID = _winreg.EnumValue(_key1, 1)[0]
        _key2 = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, '%s\shell\open\command' % _progID)
        _cmd = _winreg.QueryValueEx(_key2, None)[0]
        editor = _cmd.replace('%1', '')
        # Notepad is even worse than our Tkinter editor.
        if editor.lower().endswith('notepad.exe'):
            editor = None
    except:
        #raise
        editor = None
else:
    editor = None

# Warning: DO NOT use an editor which doesn't support Unicode to edit pages!
# You will BREAK non-ASCII symbols!
editor_encoding = 'utf-8'

# The temporary file name extension can be set in order to use syntax
# highlighting in your text editor.
editor_filename_extension = 'wiki'

############## LOGFILE SETTINGS ##############

# Defines for which scripts a logfile should be enabled. Logfiles will be
# saved in the 'logs' subdirectory.
# Example:
#     log = ['interwiki', 'weblinkchecker', 'table2wiki']
# It is also possible to enable logging for all scripts, using this line:
#     log = ['*']
# To disable all logging, use this:
#     log = []
# Per default, logging of interwiki.py is enabled because its logfiles can
# be used to generate so-called warnfiles.
log = ['interwiki']
# filename defaults to modulename-bot.log
logfilename = None
# set to 1 (or higher) to generate "informative" messages to terminal
verbose_output = 0
# if True, include a lot of debugging info in logfile
# (overrides log setting above)
debug_log = []

############## INTERWIKI SETTINGS ##############

# Should interwiki.py report warnings for missing links between foreign
# languages?
interwiki_backlink = True

# Should interwiki.py display every new link it discovers?
interwiki_shownew = True

# Should interwiki.py output a graph PNG file on conflicts?
# You need pydot for this: http://dkbza.org/pydot.html
interwiki_graph = False

# Specifies that the robot should process that amount of subjects at a time,
# only starting to load new pages in the original language when the total
# falls below that number. Default is to process (at least) 100 subjects at
# once.
interwiki_min_subjects = 100

# If interwiki graphs are enabled, which format(s) should be used?
# Supported formats include png, jpg, ps, and svg. See:
# http://www.graphviz.org/doc/info/output.html
# If you want to also dump the dot files, you can use this in your
# user-config.py:
# interwiki_graph_formats = ['dot', 'png']
# If you need a PNG image with an HTML image map, use this:
# interwiki_graph_formats = ['png', 'cmap']
# If you only need SVG images, use:
# interwiki_graph_formats = ['svg']
interwiki_graph_formats = ['png']

# You can post the contents of your autonomous_problems.dat to the wiki,
# e.g. to http://de.wikipedia.org/wiki/Wikipedia:Interwiki-Konflikte .
# This allows others to assist you in resolving interwiki problems.
# To help these people, you can upload the interwiki graphs to your
# webspace somewhere. Set the base URL here, e.g.:
# 'http://www.example.org/~yourname/interwiki-graphs/'
interwiki_graph_url = None

# Save file with local articles without interwikis.
without_interwiki = False

############## SOLVE_DISAMBIGUATION SETTINGS ############
#
# Set disambiguation_comment[FAMILY][LANG] to a non-empty string to override
# the default edit comment for the solve_disambiguation bot.
# Use %s to represent the name of the disambiguation page being treated.
# Example:
#
# disambiguation_comment['wikipedia']['en'] = \
#    "Robot-assisted disambiguation ([[WP:DPL|you can help!]]): %s"

sort_ignore_case = False

############## IMAGE RELATED SETTINGS ##############
# If you set this to True, images will be uploaded to Wikimedia
# Commons by default.
upload_to_commons = False

############## SETTINGS TO AVOID SERVER OVERLOAD ##############

# Slow down the robot such that it never requests a second page within
# 'minthrottle' seconds. This can be lengthened if the server is slow,
# but never more than 'maxthrottle' seconds. However - if you are running
# more than one bot in parallel the times are lengthened.
# By default, the get_throttle is turned off, and 'maxlag' is used to
# control the rate of server access.  Set minthrottle to non-zero to use a
# throttle on read access.
minthrottle = 0
maxthrottle = 10

# Slow down the robot such that it never makes a second page edit within
# 'put_throttle' seconds.
put_throttle = 10

# Sometimes you want to know when a delay is inserted. If a delay is larger
# than 'noisysleep' seconds, it is logged on the screen.
noisysleep = 3.0

# Defer bot edits during periods of database server lag.  For details, see
# http://www.mediawiki.org/wiki/Maxlag_parameter
# You can set this variable to a number of seconds, or to None (or 0) to
# disable this behavior.  Higher values are more aggressive in seeking
# access to the wiki.
# Non-Wikimedia wikis may or may not support this feature; for families
# that do not use it, it is recommended to set minthrottle (above) to
# at least 1 second.
maxlag = 5

# Maximum of pages which can be retrieved by special pages. Increase this if
# you heavily use redirect.py with action "double", and especially if you're
# running solve_disambiguation.py with the -primary argument.
special_page_limit = 500

############## TABLE CONVERSION BOT SETTINGS ##############

# will split long paragraphs for better reading the source.
# only table2wiki.py use it by now
splitLongParagraphs = False
# sometimes HTML-tables are indented for better reading.
# That can do very ugly results.
deIndentTables = True
# table2wiki.py works quite stable, so you might switch to True
table2wikiAskOnlyWarnngs = True
table2wikiSkipWarnings = False

############## WEBLINK CHECKER SETTINGS ##############

# How many external links should weblinkchecker.py check at the same time?
# If you have a fast connection, you might want to increase this number so
# that slow servers won't slow you down.
max_external_links = 50

report_dead_links_on_talk = False

############## DATABASE SETTINGS ##############
db_hostname = 'localhost'
db_username = 'wikiuser'
db_password = ''

############## SEARCH ENGINE SETTINGS ##############

# Some scripts allow querying Google via the Google Web API. To use this feature,
# you must install the pyGoogle module from http://pygoogle.sf.net/ and have a
# Google Web API license key. Note that Google doesn't give out license keys
# anymore.
google_key = ''

# Some scripts allow using the Yahoo! Search Web Services. To use this feature,
# you must install the pYsearch module from http://pysearch.sourceforge.net/
# and get a Yahoo AppID from http://developer.yahoo.com
yahoo_appid = ''

# To use Windows Live Search web service you must get an AppID from
# http://search.msn.com/developer
msn_appid = ''

############## COPYRIGHT SETTINGS ##############

# Enable/disable search engine in copyright.py script
copyright_google = True
copyright_yahoo = True
copyright_msn = False

# Perform a deep check, loading URLs to search if 'Wikipedia' is present.
# This may be useful to improve number of correct results. If you haven't
# a fast connection, you might want to keep they disabled.
copyright_check_in_source_google = False
copyright_check_in_source_yahoo = False
copyright_check_in_source_msn = False

# Web pages may content a Wikipedia text without 'Wikipedia' word but with
# typical '[edit]' tag result of copy & paste procedure. You can want no
# report for this kind of URLs, even if they are copyright violation.
# However, when enabled these URLs are logged in a file.

copyright_check_in_source_section_names = False

# Limit number of queries for page.
copyright_max_query_for_page = 25

# Skip a specified number of queries
copyright_skip_query = 0

# Number of attempts on connection error.
copyright_connection_tries = 10

# Behavior if an exceeded error occur.
#
# Possibilities:
#
#    0 = None
#    1 = Disable search engine
#    2 = Sleep (default)
#    3 = Stop

copyright_exceeded_in_queries = 2
copyright_exceeded_in_queries_sleep_hours = 6

# Append last modified date of URL to script result
copyright_show_date = True

# Append length of URL to script result
copyright_show_length = True

# By default the script try to identify and skip text that contents a wide
# comma separated list or only numbers. But sometimes that might be the
# only part unmodified of a slightly edited and not otherwise reported
# copyright violation. You can disable this feature to try to increase
# number of results.

copyright_economize_query = True

############## HTTP SETTINGS ##############
# Use a persistent http connection. An http connection has to be established
# only once per site object, making stuff a whole lot faster. Do NOT EVER
# use this if you share Site objects across threads without proper locking.
## DISABLED FUNCTION. Setting this variable will not have any effect.
persistent_http = False

# Default socket timeout. Set to None to disable timeouts.
socket_timeout = 120  # set a pretty long timeout just in case...


############## FURTHER SETTINGS ##############

# The bot can make some additional changes to each page it edits, e.g. fix
# whitespace or positioning of interwiki and category links.

# This is an experimental feature; handle with care and consider re-checking
# each bot edit if enabling this!
cosmetic_changes = False

# If cosmetic changes are switched on, and you also have several accounts at
# projects where you're not familiar with the local conventions, you probably
# only want the bot to do cosmetic changes on your "home" wiki which you
# specified in config.mylang and config.family.
# If you want the bot to also do cosmetic changes when editing a page on a
# foreign wiki, set cosmetic_changes_mylang_only to False, but be careful!
cosmetic_changes_mylang_only = True

# End of configuration section
# ============================
# System-level and User-level changes.
# Store current variables and their types.
_glv={}
_glv.update(globals())
_gl=_glv.keys()
_tp={}
for _key in _gl:
    if _key[0]!='_':
        _tp[_key]=type(globals()[_key])

# Get the user files
_thislevel=0
_fns=[os.path.join(_base_dir, "user-config.py")]
for _filename in _fns:
    _thislevel += 1
    if os.path.exists(_filename):
        _filestatus=os.stat(_filename)
        _filemode=_filestatus[0]
        _fileuid=_filestatus[4]
        if (__sys.platform=='win32' or _fileuid==os.getuid() or _fileuid==0):
            if __sys.platform=='win32' or _filemode&002==0:
                execfile(_filename)
            else:
                print "WARNING: Skipped '%(fn)s': writeable by others."\
                      % {'fn' :_filename}
        else:
            print "WARNING: Skipped '%(fn)s': owned by someone else."\
                  % {'fn' :_filename}

# Test for obsoleted and/or unknown variables.
for _key in globals().iterkeys():
    if _key[0]=='_':
        pass
    elif _key in _gl:
        nt=type(globals()[_key])
        ot=_tp[_key]
        if nt==ot or nt==type(None) or ot==type(None):
            pass
        elif nt==type(1) and ot==type(1.0):
            pass
        elif ot==type(1) and nt==type(1.0):
            pass
        elif nt==type(1) and ot==type(True):
            pass
        elif ot==type(1) and nt==type(True):
            pass
        else:
            print "WARNING: Type of '%(_key)s' changed" % locals()
            print "         %(was)s: %(old)s" % {'was': "Was", 'old': ot}
            print "         %(was)s: %(new)s" % {'now': "Now", 'new': nt}
        del nt,ot
    else:
        print \
            "Configuration variable %(_key)r is defined but unknown."\
            " Misspelled?" % locals()

# Fix up default console_encoding
if console_encoding == None:
    if __sys.platform=='win32':
        console_encoding = 'cp850'
    else:
        console_encoding = 'iso-8859-1'

# Save base_dir for use by other modules
base_dir = _base_dir

def makepath(path):
    """Return a normalized absolute version of the path argument.

    - if the given path already exists in the filesystem
      the filesystem is not modified.

    - otherwise makepath creates directories along the given path
      using the dirname() of the path. You may append
      a '/' to the path if you want it to be a directory path.

    from holger@trillke.net 2002/03/18

    """
    from os import makedirs
    from os.path import normpath, dirname, exists, abspath

    dpath = normpath(dirname(path))
    if not exists(dpath): makedirs(dpath)
    return normpath(abspath(path))

def datafilepath(*filename):
    """Return an absolute path to a data file in a standard location.

    Argument(s) are zero or more directory names, optionally followed by a
    data file name. The return path is offset to config.base_dir. Any
    directories in the path that do not already exist are created.

    """
    import os
    return makepath(os.path.join(base_dir, *filename))

def shortpath(path):
    """Return a file path relative to config.base_dir."""
    import os
    if path.startswith(base_dir):
        return path[len(base_dir) + len(os.path.sep) : ]
    return path

#
# When called as main program, list all configuration variables
#
if __name__=="__main__":
    import types
    _all=1
    for _arg in __sys.argv[1:]:
        if _arg=="modified":
            _all=0
        else:
            print "Unknown arg %(_arg)s ignored" % locals()
    _k=globals().keys()
    _k.sort()
    for _name in _k:
        if _name[0]!='_':
            if not type(globals()[_name]) in [types.FunctionType, types.ModuleType]:
                if _all or _glv[_name]!=globals()[_name]:
                    print _name,"=",repr(globals()[_name])

# cleanup all locally-defined variables

for __var in globals().iterkeys():
    if __var.startswith("_") and not __var.startswith("__"):
        del __sys.modules[__name__].__dict__[__var]

del __var, __sys
del os, re

