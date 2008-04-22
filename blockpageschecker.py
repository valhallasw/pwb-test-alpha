# -*- coding: utf-8  -*-
"""
This is a script originally written by Wikihermit and then rewritten by Filnik,
to delete the templates used to warn in the pages that a page is blocked,
when the page isn't blocked at all. Indeed, very often sysops block the pages
for a setted time but then the forget to delete the warning! This script is useful
if you want to delete those useless warning left in these pages.

Parameters:

These command line parameters can be used to specify which pages to work on:

&params;

-xml              Retrieve information from a local XML dump (pages-articles
                  or pages-meta-current, see http://download.wikimedia.org).
                  Argument can also be given as "-xml:filename".

-page             Only edit a specific page.
                  Argument can also be given as "-page:pagetitle". You can
                  give this parameter multiple times to edit multiple pages.

-protectedpages:  Check all the blocked pages (useful when you have not categories
                  or when you have problems with them. (add the namespace after ":" where
                  you want to check - default checks all protected pages)

Furthermore, the following command line parameters are supported:

-always         Doesn't ask every time if the bot should make the change or not, do it always.

-debug          When the bot can't delete the template from the page (wrong regex or something like that)
                it will ask you if it should open the page on your browser.
                (attention: pages included may give false positives..)

-move           The bot will check if the page is blocked also for the move option, not only for edit

--- Warning! ---
You have to edit this script in order to add your preferences
otherwise the script won't work!

If you have problems, ask on botwiki ( http://botwiki.sno.cc )
or on IRC (#pywikipediabot)

--- Example of how to use the script ---

python blockpageschecker.py -always

python blockpageschecker.py -cat:Geography -always

python blockpageschecker.py -debug -protectedpages:4

"""
#
# (C) Monobi a.k.a. Wikihermit, 2007
# (C) Filnik, 2007-2008
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: blockpageschecker.py,v 1.1 2007/12/7 19.23.00 filnik Exp$'
#

import re, webbrowser
import wikipedia, catlib, pagegenerators, config

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;':     pagegenerators.parameterHelp,
}

#######################################################
#--------------------- PREFERENCES -------------------#
################### -- Edit below! -- #################

# Added a new feature! Please update and add the settings in order
# to improve the intelligence of this script ;-)
# Regex to get the semi-protection template
templateSemiProtection = {
            'en': None,
            'it':[r'{\{(?:[Tt]emplate:|)[Aa]vvisobloccoparziale(?:|[ _]scad\|.*?|\|.*?)\}\}',
                  r'{\{(?:[Tt]emplate:|)[Aa]bp(?:|[ _]scad\|(?:.*?))\}\}'],
            'fr': [ur'\{\{(?:[Tt]emplate:|[Mm]odèle:|)[Ss]emi[- ]?protection(|[^\}]*)\}\}'],
            'ja':[ur'\{\{(?:[Tt]emplate:|)半保護(?:[Ss]|)(?:\|.+|)\}\}(\n+?|)'],
            'zh':[ur'\{\{(?:[Tt]emplate:|)Protected|(?:[Ss]|[Ss]emi|半)(?:\|.+|)\}\}(\n+?|)',ur'\{\{(?:[Tt]emplate:|)Mini-protected|(?:[Ss]|[Ss]emi|半)(?:\|.+|)\}\}(\n+?|)',ur'\{\{(?:[Tt]emplate:|)Protected-logo|(?:[Ss]|[Ss]emi|半)(?:\|.+|)\}\}(\n+?|)'],
            }
# Regex to get the total-protection template
templateTotalProtection = {
            'en': None, 
            'it':[r'{\{(?:[Tt]emplate:|)[Aa]vvisoblocco(?:|[ _]scad\|(?:.*?)|minaccia|cancellata)\}\}',
                  r'{\{(?:[Tt]emplate:|)(?:[Cc][Tt]|[Cc]anc fatte|[Cc][Ee].*?)\}\}', r'<div class="toccolours[ _]itwiki[ _]template[ _]avviso">(?:\s|\n)*?[Qq]uesta pagina'],
            'fr':[ur'\{\{(?:[Tt]emplate:|[Mm]odèle:|)[Pp]rotection(|[^\}]*)\}\}',
                 ur'\{\{(?:[Tt]emplate:|[Mm]odèle:|)(?:[Pp]age|[Aa]rchive|[Mm]odèle) protégée?(|[^\}]*)\}\}'],
            'ja':[ur'\{\{(?:[Tt]emplate:|)保護(?:[Ss]|)(?:\|.+|)\}\}(\n+?|)'],
            'zh':[r'\{\{(?:[Tt]emplate:|)Protected|(?:[Nn]|[Nn]ormal)(?:\|.+|)\}\}(\n+?|)',r'\{\{(?:[Tt]emplate:|)Mini-protected|(?:[Nn]|[Nn]ormal)(?:\|.+|)\}\}(\n+?|)',r'\{\{(?:[Tt]emplate:|)Protected-logo|(?:[Nn]|[Nn]ormal)(?:\|.+|)\}\}(\n+?|)'],
            }
# Regex to get the semi-protection move template
templateSemiMoveProtection = {
            'en': None, 
            'it':[r'{\{(?:[Tt]emplate:|)[Aa]vvisobloccospostamento(?:|[ _]scad\|.*?|\|.*?)\}\}'],
            'ja':[ur'\{\{(?:[Tt]emplate:|)移動半保護(?:[Ss]|)(?:\|.+|)\}\}(\n+?|)'],
            'zh':[r'\{\{(?:[Tt]emplate:|)Protected|(?:MS|ms)(?:\|.+|)\}\}(\n+?|)',r'\{\{(?:[Tt]emplate:|)Mini-protected|(?:MS|ms)(?:\|.+|)\}\}(\n+?|)',r'\{\{(?:[Tt]emplate:|)Protected-logo|(?:MS|ms)(?:\|.+|)\}\}(\n+?|)'],
            }
# Regex to get the total-protection move template 
templateTotalMoveProtection = {
            'en': None, 
            'it':[r'{\{(?:[Tt]emplate:|)[Aa]vvisobloccospostamento(?:|[ _]scad\|.*?|\|.*?)\}\}'],
            'ja':[ur'\{\{(?:[Tt]emplate:|)移動保護(?:[Ss]|)(?:\|.+|)\}\}(\n+?|)'],
            'zh':[ur'\{\{(?:[Tt]emplate:|)Protected|(?:[Mm]|[Mm]ove|移[動动])(?:\|.+|)\}\}(\n+?|)',ur'\{\{(?:[Tt]emplate:|)Mini-protected|(?:[Mm]|[Mm]ove|移[動动])(?:\|.+|)\}\}(\n+?|)',ur'\{\{(?:[Tt]emplate:|)Protected-logo|(?:[Mm]|[Mm]ove|移[動动])(?:\|.+|)\}\}(\n+?|)'],
            }
# Array: 0 => Semi-block, 1 => Total Block, 2 => Semi-Move, 3 => Total-Move
templateNoRegex = {
            'it':['{{Avvisobloccoparziale}}', '{{Avvisoblocco}}', None, None],
            'fr':['{{Semi-protection}}', '{{Protection}}', None, None],
            'ja':[u'{{半保護}}', u'{{保護}}', u'{{移動半保護}}',u'{{移動保護}}'],
            'zh':[u'{{Protected/semi}}',u'{{Protected}}',u'{{Protected/ms}}',u'{{Protected/move}}'],
            }

# Category where the bot will check
categoryToCheck = {
            'en':[u'Category:Protected'],
            'fr':[u'Category:Page semi-protégée', u'Category:Page protégée', u'Catégorie:Article protégé'],
            'he':[u'קטגוריה:ויקיפדיה: דפים מוגנים', u'קטגוריה:ויקיפדיה: דפים מוגנים חלקית'],
            'it':[u'Categoria:Pagine semiprotette', u'Categoria:Voci_protette'],
            'ja':[u'Category:編集保護中の記事',u'Category:編集半保護中の記事',
                u'Category:移動保護中の記事',],
            'pt':[u'Category:!Páginas protegidas', u'Category:!Páginas semiprotegidas'],
            'zh':[u'Category:被保护的页面',u'Category:被保護的模板',u'Category:暂时不能移动的页面',
                u'Category:被半保护的页面',],
            }
# Comment used when the Bot edits
comment = {
            'en':u'Bot: Deleting out-dated template',
            'fr':u'Robot: Mise à jour des bandeaux de protection',
            'he':u'בוט: מסיר תבנית שעבר זמנה',
            'it':u'Bot: Tolgo o sistemo template di avviso blocco',
            'ja':u'ロボットによる: 保護テンプレート除去',
            'pt':u'Bot: Retirando predefinição de proteção',
            'zh':u'機器人: 移除過期的保護模板',
            }
# Check list to block the users that haven't set their preferences
project_inserted = ['en', 'fr', 'it', 'ja', 'pt', 'zh']

#######################################################
#------------------ END PREFERENCES ------------------#
################## -- Edit above! -- ##################

def understandBlock(text, TTP, TSP, TSMP, TTMP):
    """ Understand if the page is blocked and if it has the right template """
    for catchRegex in TTP: # TTP = templateTotalProtection
        resultCatch = re.findall(catchRegex, text)
        if resultCatch:
            return ('sysop-total', catchRegex)
    for catchRegex in TSP:
        resultCatch = re.findall(catchRegex, text)
        if resultCatch:
            return ('autoconfirmed-total', catchRegex)
    if TSMP != None and TTMP != None and TTP != TTMP and TSP != TSMP:
        for catchRegex in TSMP:
            resultCatch = re.findall(catchRegex, text)
            if resultCatch:
                return ('sysop-move', catchRegex)
        for catchRegex in TTMP:
            resultCatch = re.findall(catchRegex, text)
            if resultCatch:
                return ('autoconfirmed-move', catchRegex)
    return ('editable', r'\A\n') # If editable means that we have no regex, won't change anything with this regex

def ProtectedPagesData(namespace = None):
    """ Yield all the pages blocked, using Special:ProtectedPages """
    # Avoid problems of encoding and stuff like that, let it divided please
    url = '/w/index.php?title=Special:ProtectedPages&type=edit&level=0'
    if namespace != None: # /!\ if namespace seems simpler, but returns false when ns=0
        url += '&namespace=%s' % namespace    
    site = wikipedia.getSite()
    parser_text = site.getUrl(url)
    while 1:
        #<li><a href="/wiki/Pagina_principale" title="Pagina principale">Pagina principale</a>‎ <small>(6.522 byte)</small> ‎(protetta)</li>
        m = re.findall(r'<li><a href=".*?" title=".*?">(.*?)</a>.*?<small>\((.*?)\)</small>.*?\((.*?)\)</li>', parser_text)
        for data in m:
            title = data[0]
            size = data[1]
            status = data[2]
            yield (title, size, status)
        nextpage = re.findall(r'<.ul>\(.*?\).*?\(.*?\).*?\(<a href="(.*?)".*?</a>\) +?\(<a href=', parser_text)
        if nextpage != []:
            parser_text = site.getUrl(nextpage[0].replace('&amp;', '&'))
            continue
        else:
            break
        
def ProtectedPages(namespace = 0):
    """ Return only the wiki page object and not the tuple with all the data as above """
    for data in ProtectedPagesData(namespace):
        yield wikipedia.Page(wikipedia.getSite(), data[0])

def debugQuest(site, page):
    quest = wikipedia.input(u'Do you want to open the page on your [b]rowser, [g]ui or [n]othing?')
    pathWiki = site.family.nicepath(site.lang)
    url = 'http://%s%s%s?&redirect=no' % (wikipedia.getSite().hostname(), pathWiki, page.urlname())
    while 1:
        if quest.lower() in ['b', 'B']:                    
            webbrowser.open(url)
            break
        elif quest.lower() in ['g', 'G']:
            import editarticle
            editor = editarticle.TextEditor()
            text = editor.edit(page.get())
            break
        elif quest.lower() in ['n', 'N']:
            break
        else:
            wikipedia.output(u'wrong entry, type "b", "g" or "n"')
            continue

def main():
    """ Main Function """
    # Loading the comments
    global categoryToCheck; global comment; global project_inserted
    if config.mylang not in project_inserted:
        wikipedia.output(u"Your project is not supported by this script. You have to edit the script and add it!")
        wikipedia.stopme()
    # always, define a generator to understand if the user sets one, defining what's genFactory
    always = False; generator = False; debug = False
    moveBlockCheck = False; genFactory = pagegenerators.GeneratorFactory()
    # To prevent Infinite loops
    errorCount = 0
    # Loading the default options.
    for arg in wikipedia.handleArgs():
        if arg == '-always':
            always = True
        elif arg == '-move':
            moveBlockCheck = True
        elif arg == '-debug':
            debug = True
        elif arg.startswith('-protectedpages'):
            if len(arg) == 15:
                generator = ProtectedPages()
            else:
                generator = ProtectedPages(int(arg[16:]))
        elif arg.startswith('-page'):
            if len(arg) == 5:
                generator = [wikipedia.Page(wikipedia.getSite(), wikipedia.input(u'What page do you want to use?'))]
            else:
                generator = [wikipedia.Page(wikipedia.getSite(), arg[6:])]
        else:
            generator = genFactory.handleArg(arg)
    # Load the right site
    site = wikipedia.getSite()
    # Take the right templates to use, the category and the comment
    TSP = wikipedia.translate(site, templateSemiProtection)
    TTP = wikipedia.translate(site, templateTotalProtection)
    TSMP = wikipedia.translate(site, templateSemiMoveProtection)
    TTMP = wikipedia.translate(site, templateTotalMoveProtection)
    TNR = wikipedia.translate(site, templateNoRegex)
    
    category = wikipedia.translate(site, categoryToCheck)
    commentUsed = wikipedia.translate(site, comment)
    if not generator:
        generator = list()
        wikipedia.output(u'Loading categories...')
        # Define the category if no other generator has been setted
        for CAT in category:
            cat = catlib.Category(site, CAT)
            # Define the generator
            gen = pagegenerators.CategorizedPageGenerator(cat)
            for pageCat in gen:
                generator.append(pageCat)
        wikipedia.output(u'Categories loaded, start!')
    # Main Loop
    preloadingGen = pagegenerators.PreloadingGenerator(generator, pageNumber = 60)
    for page in preloadingGen:
        pagename = page.aslink()
        wikipedia.output('Loading %s...' % pagename)
        try:
            text = page.get()
            restrictions = page.getRestrictions()
        except wikipedia.NoPage:
            wikipedia.output("%s doesn't exist! Skipping..." % pagename)
            continue
        except wikipedia.IsRedirectPage:
            wikipedia.output("%s is a redirect! Skipping..." % pagename)
            if debug:
                debugQuest(site, page)
            continue
        if not page.canBeEdited():
            wikipedia.output("%s is protected : this account can't edit it! Skipping..." % pagename)
            continue        
        # Understand, according to the template in the page, what should be the protection
        # and compare it with what there really is.
        TemplateInThePage = understandBlock(text, TTP, TSP, TSMP, TTMP)
        # Only to see if the text is the same or not...
        oldtext = text
        editRestr = restrictions['edit']
        # keep track of the changes for each step (edit then move)
        changes = -1

        if not editRestr:
            # page is not edit-protected
            # Deleting the template because the page doesn't need it.
            replaceToPerform = u'|'.join(TTP + TSP)
            texti, changes = re.subn('(?:<noinclude>|)(%s)(?:</noinclude>|)' % replaceToPerform, '', text)
            wikipedia.output(u'The page is editable for all, deleting the template...')

        elif editRestr[0] == 'sysop':
            # total edit protection         
            if TemplateInThePage[0] == 'sysop-total' and TTP != None:
                msg = 'The page is protected to the sysop'
                if not moveBlockCheck:
                    msg += ', skipping...'
                wikipedia.output(msg)
            else:
                wikipedia.output(u'The page is protected to the sysop, but the template seems not correct. Fixing...')
                text, changes = re.subn(TemplateInThePage[1], TNR[1], text)

        elif TSP != None:
            # implicitely editRestr[0] = 'autoconfirmed', edit-Semi-protection
            if TemplateInThePage[0] == 'autoconfirmed-total':                    
                msg = 'The page is editable only for the autoconfirmed users'
                if not moveBlockCheck:
                    msg += ', skipping...'
                wikipedia.output(msg)
            else:
                wikipedia.output(u'The page is editable only for the autoconfirmed users, but the template seems not correct. Fixing...')
                text, changes = re.subn(TemplateInThePage[1], TNR[0], text)

        if changes == 0:
            # We tried to fix edit-protection templates, but it did not work.
            wikipedia.output('Warning : No edit-protection template could be found')
        
        if moveBlockCheck:
            # checking move protection now
            moveRestr = restrictions['move']
            changes = -1

            if not moveRestr:
                wikipedia.output(u'The page is movable for all, deleting the template...')
                # Deleting the template because the page doesn't need it.
                replaceToPerform = u'|'.join(TSMP + TTMP)
                text, changes = re.subn('(?:<noinclude>|)(%s)(?:</noinclude>|)' % replaceToPerform, '', text)

            elif moveRestr[0] == 'sysop':
                # move-total-protection
                if TemplateInThePage[0] == 'sysop-move' and TTMP != None:
                    wikipedia.output(u'The page is protected from moving to the sysop, skipping...')
                else:
                    wikipedia.output(u'The page is protected from moving to the sysop, but the template seems not correct. Fixing...')
                    text, changes = re.subn(TemplateInThePage[1], TNR[3], text)

            elif TSMP != None:
                # implicitely moveRestr[0] = 'autoconfirmed', move-semi-protection
                if TemplateInThePage[0] == 'autoconfirmed-move':
                    wikipedia.output(u'The page is movable only for the autoconfirmed users, skipping...')
                else:
                    wikipedia.output(u'The page is movable only for the autoconfirmed users, but the template seems not correct. Fixing...')
                    text, changes = re.subn(TemplateInThePage[1], TNR[2], text)

            if changes == 0:
                # We tried to fix move-protection templates, but it did not work.
                wikipedia.output('Warning : No move-protection template could be found')


        if oldtext != text:
            # Ok, asking if the change has to be performed and do it if yes.
            wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
            wikipedia.showDiff(oldtext, text)
            choice = ''
            while 1:
                if not always:
                    choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                if choice.lower() in ['a', 'all']:
                    always = True
                if choice.lower() in ['n', 'no']:
                    break
                if choice.lower() in ['y', 'yes'] or always:
                    try:
                        page.put(text, commentUsed, force=True)
                    except wikipedia.EditConflict:
                        wikipedia.output(u'Edit conflict! skip!')
                        break
                    except wikipedia.ServerError:
                        # Sometimes there is this error that's quite annoying because
                        # can block the whole process for nothing. 
                        errorCount += 1
                        if errorCount < 5:
                            wikipedia.output(u'Server Error! Wait..')
                            time.sleep(3)
                            continue
                        else:
                            # Prevent Infinite Loops
                            raise wikipedia.ServerError(u'Fifth Server Error!')
                    except wikipedia.SpamfilterError, e:
                        wikipedia.output(u'Cannot change %s because of blacklist entry %s' % (page.title(), e.url))
                        break
                    except wikipedia.PageNotSaved, error:
                        wikipedia.output(u'Error putting page: %s' % (error.args,))
                        break
                    except wikipedia.LockedPage:
                        wikipedia.output(u'The page is still protected. Skipping...')
                        break
                    else:
                        # Break only if the errors are one after the other
                        errorCount = 0
                        break
                    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
