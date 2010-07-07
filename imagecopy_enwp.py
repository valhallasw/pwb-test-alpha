# -*- coding: utf-8 -*-
"""
Script to copy self published files from the English Wikipedia to Wikimedia Commons.

This bot is based on imagecopy.py and intended to be used to empty out http://en.wikipedia.org/wiki/Category:Self-published_work

This bot uses a graphical interface and may not work from commandline
only environment.

Examples

Work on a single file
 python imagecopy.py -page:file:<filename>
Work on all images in a category:<cat>
 python imagecopy.py -cat:<cat>
Work on all images which transclude a template
 python imagecopy.py -transcludes:<template>

See pagegenerators.py for more ways to get a list of images.
By default the bot works on your home wiki (set in user-config)

This is a first test version and should be used with care.

Use -nochecktemplate if you don't want to add the check template. Be sure to check it yourself.

Todo:
*Queues with threads have to be implemented for the information collecting part and for the upload part.
*Categories are now on a single line. Something like hotcat would be nice.

"""
#
# Based on upload.py by:
# (C) Rob W.W. Hooft, Andre Engels 2003-2007
# (C) Wikipedian, Keichwa, Leogregianin, Rikwade, Misza13 2003-2007
#
# New bot by:
# (C) Kyle/Orgullomoore, Siebrand Mazeland 2007
#
# Another rewrite by:
#  (C) Multichill 2008
#
# English Wikipedia specific bot by:
#  (C) Multichill 2010
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'
#

from Tkinter import *
import os, sys, re, codecs
import urllib, httplib, urllib2
import webbrowser
import time, threading
import wikipedia, config, socket
import pagegenerators, add_text
import imagerecat
from datetime import datetime
from upload import *
from image import *
NL=''

nowCommonsTemplate = {
    'en': u'{{NowCommons|1=File:%s|date=~~~~~|reviewer={{subst:REVISIONUSER}}}}',
}

nowCommonsMessage = {
    'en': u'File is now available on Wikimedia Commons.',
}

moveToCommonsTemplate = {
    'en': [u'Commons ok', u'Copy to Wikimedia Commons', u'Move to commons', u'Movetocommons', u'To commons', u'Copy to Wikimedia Commons by BotMultichill'],
}

imageMoveMessage = {
    'en': u'[[:File:%s|File]] moved to [[:commons:File:%s|commons]].',
}

skipTemplates = [u'Db-f1',
                 u'Db-f2',
                 u'Db-f3',
                 u'Db-f7',
                 u'Db-f8',
                 u'Db-f9',
                 u'Db-f10',
                 u'NowCommons',
                 u'CommonsNow',
                 u'Nowcommons',
                 u'NowCommonsThis',
                 u'Nowcommons2',
                 u'NCT',
                 u'Nowcommonsthis',
                 u'Moved to commons',
                 u'Now Commons',
                 u'Now at commons',
                 u'Db-nowcommons',
                 u'WikimediaCommons',
                 u'Now commons',
                 u'Di-no source',
                 u'Di-no license',
                 u'Di-no permission',
                 u'Di-orphaned fair use',
                 u'Di-no source no license',
                 u'Di-replaceable fair use',
                 u'Di-no fair use rationale',
                 u'Di-disputed fair use rationale',
                 u'Puf',
                 u'PUI',
                 u'Pui',
                 u'Ffd',
                 u'PD-user', # Only the self templates are supported for now.
                 ]
                 

licenseTemplates = [(u'\{\{(self|self2)\|([^\}]+)\}\}', u'{{Self|\\2|author=[[:%(lang)s:User:%(author)s|%(author)s]] at [http://%(lang)s.%(family)s.org %(lang)s.%(family)s]}}'),
                    (u'\{\{(GFDL-self|GFDL-self-no-disclaimers)\|([^\}]+)\}\}', u'{{Self|GFDL|\\2|author=[[:%(lang)s:User:%(author)s|%(author)s]] at [http://%(lang)s.%(family)s.org %(lang)s.%(family)s]}}'),
                    (u'\{\{GFDL-self-with-disclaimers\|([^\}]+)\}\}', u'{{Self|GFDL-with-disclaimers|\\1|author=[[:%(lang)s:User:%(author)s|%(author)s]] at [http://%(lang)s.%(family)s.org %(lang)s.%(family)s]}}'),
                    (u'\{\{PD-self(\|date=[^\}]+)\}\}', u'{{PD-user-w|%(lang)s|%(family)s|%(author)s}}'),
                    #Multilicense replacing placeholder
                    (u'\{\{Multilicense replacing placeholder new(\|class=[^\}]+)\}\}', u'{{Self|GFDL|Cc-by-sa-3.0,2.5,2.0,1.0|author=[[:%(lang)s:User:%(author)s|%(author)s]] at [http://%(lang)s.%(family)s.org %(lang)s.%(family)s]}}'),
                    ]

sourceGarbage =     [u'== Summary ==',
                     u'== Licensing:? ==',
                    ]

class Tkdialog:
    def __init__(self, imagepage, currentcontent):
        self.root=Tk()
        #"%dx%d%+d%+d" % (width, height, xoffset, yoffset)
        #Always appear the same size and in the bottom-left corner
        self.root.geometry("1000x400+100-100")
        self.root.title(imagepage.titleWithoutNamespace())


        self.url=imagepage.permalink()
        self.scrollbar=Scrollbar(self.root, orient=VERTICAL)

        self.old_description=Text(self.root)
        self.old_description.insert(END, imagepage.get().encode('utf-8'))
        self.old_description.config(state=DISABLED, height=8, width=140, padx=0, pady=0, wrap=WORD, yscrollcommand=self.scrollbar.set)

        self.scrollbar.config(command=self.old_description.yview)

        self.filename = imagepage.titleWithoutNamespace()

        (self.description,
        self.date,
        self.source,
        self.author,
        self.licensetemplate,
        self.categories) = currentcontent
        self.skip = False

        self.old_description_label=Label(self.root,text=u'The old description was : ')
        self.new_description_label=Label(self.root,text=u'The new fields are : ')
        self.filename_label=Label(self.root,text=u'Filename : ')
        self.information_description_label=Label(self.root,text=u'Description : ')
        self.information_date_label=Label(self.root,text=u'Date : ')
        self.information_source_label=Label(self.root,text=u'Source : ')
        self.information_author_label=Label(self.root,text=u'Author : ')
        self.information_licensetemplate_label=Label(self.root,text=u'License : ')
        self.information_categories_label=Label(self.root,text=u'Categories : ')

        self.filename_field=Entry(self.root)
        self.information_description=Entry(self.root)
        self.information_date=Entry(self.root)
        self.information_source=Entry(self.root)
        self.information_author=Entry(self.root)
        self.information_licensetemplate=Entry(self.root)
        self.information_categories=Entry(self.root)

        self.field_width=120

        self.filename_field.config(width=self.field_width)
        self.information_description.config(width=self.field_width)
        self.information_date.config(width=self.field_width)
        self.information_source.config(width=self.field_width)
        self.information_author.config(width=self.field_width)
        self.information_licensetemplate.config(width=self.field_width)
        self.information_categories.config(width=self.field_width)


        self.filename_field.insert(0, self.filename)
        self.information_description.insert(0, self.description)
        self.information_date.insert(0, self.date)
        self.information_source.insert(0, self.source)
        self.information_author.insert(0, self.author)
        self.information_licensetemplate.insert(0, self.licensetemplate)
        self.information_categories.insert(0, self.categories)

        self.browserButton=Button(self.root, text='View in browser', command=self.openInBrowser)
        self.skipButton=Button(self.root, text="Skip", command=self.skipFile)
        self.okButton=Button(self.root, text="OK", command=self.okFile)

        ##Start grid
        self.old_description_label.grid(row=0, column=0, columnspan=3)

        self.old_description.grid(row=1, column=0, columnspan=3)
        self.scrollbar.grid(row=1, column=3)
        self.new_description_label.grid(row=2, column=0, columnspan=3)
        
        self.filename_label.grid(row=3, column=0)
        self.information_description_label.grid(row=4, column=0)
        self.information_date_label.grid(row=5, column=0)
        self.information_source_label.grid(row=6, column=0)
        self.information_author_label.grid(row=7, column=0)
        self.information_licensetemplate_label.grid(row=8, column=0)
        self.information_categories_label.grid(row=9, column=0)

        self.filename_field.grid(row=3, column=1, columnspan=3)
        self.information_description.grid(row=4, column=1, columnspan=3)
        self.information_date.grid(row=5, column=1, columnspan=3)
        self.information_source.grid(row=6, column=1, columnspan=3)
        self.information_author.grid(row=7, column=1, columnspan=3)
        self.information_licensetemplate.grid(row=8, column=1, columnspan=3)
        self.information_categories.grid(row=9, column=1, columnspan=3)

        self.okButton.grid(row=10, column=3, rowspan=2)
        self.skipButton.grid(row=10, column=2, rowspan=2)
        self.browserButton.grid(row=10, column=1, rowspan=2)

    def okFile(self):
        '''
        The user pressed the OK button.
        '''
        self.filename=self.filename_field.get()
        self.description=self.information_description.get()
        self.date=self.information_date.get()
        self.source=self.information_source.get()
        self.author=self.information_author.get()
        self.licensetemplate=self.information_licensetemplate.get()
        self.categories=self.information_categories.get()
        
        self.root.destroy()

    def skipFile(self):
        '''
        The user pressed the Skip button.
        '''
        self.skip=1
        self.root.destroy()

    def openInBrowser(self):
        '''
        The user pressed the View in browser button.
        '''
        webbrowser.open(self.url)

    def add2autoskip(self):
        '''
        The user pressed the Add to AutoSkip button.
        '''
        templateid=int(self.templatelist.curselection()[0])
        template=self.templatelist.get(templateid)
        toadd=codecs.open(archivo, 'a', 'utf-8')
        toadd.write('{{'+template)
        toadd.close()
        self.skipFile()

    def getnewmetadata(self):
        '''
        Activate the dialog and return the new name and if the image is skipped.
        '''
        self.root.mainloop()
        return (self.filename, self.description, self.date, self.source, self.author, self.licensetemplate, self.categories, self.skip)


def doiskip(imagepage):
    '''
    Skip this image or not.
    Returns True if the image is on the skip list, otherwise False
    '''
    for template in imagepage.templates():
        if template in skipTemplates:
            wikipedia.output(u'Found ' + template + u' which is on the template skip list')
            return True
    return False

def getNewFields(imagepage):
    '''
    Build a new description based on the imagepage
    '''
    if u'{{Information' in imagepage.get() or u'{{information' in imagepage.get():
        (description, date, source, author) = getNewFieldsFromInformation(imagepage)
    else:
        (description, date, source, author) = getNewFieldsFromFreetext(imagepage)

    licensetemplate = getNewLicensetemplate(imagepage)
    categories = getNewCategories(imagepage)
    return (description, date, source, author, licensetemplate, categories)

def getNewFieldsFromInformation(imagepage):
    '''
    '''
    description = u''
    date = u''
    source = u''
    author = u''
    permission = u''
    other_versions = u''
    text = imagepage.get()
    # Need to add the permission field
    regexes =[u'\{\{Information[\s\r\n]*\|[\s\r\n]*description[\s\r\n]*=(?P<description>.*)\|[\s\r\n]*source[\s\r\n]*=(?P<source>.*)\|[\s\r\n]*date[\s\r\n]*=(?P<date>.*)\|[\s\r\n]*author[\s\r\n]*=(?P<author>.*)\|[\s\r\n]*permission.*=(?P<permission>[^\}]*)\|[\s\r\n]*other_versions.*=(?P<other_versions>[^\}]*)\}\}',
              u'\{\{Information[\s\r\n]*\|[\s\r\n]*description[\s\r\n]*=(?P<description>.*)\|[\s\r\n]*source[\s\r\n]*=(?P<source>.*)\|[\s\r\n]*date[\s\r\n]*=(?P<date>.*)\|[\s\r\n]*author[\s\r\n]*=(?P<author>.*)\|[\s\r\n]*other_versions.*=(?P<other_versions>[^\}]*)\}\}',              
              ]
            

    for regex in regexes:
        match =re.search(regex, text, re.IGNORECASE|re.DOTALL)
        if match:
            description = convertLinks(match.group(u'description').strip(), imagepage.site())
            date = match.group(u'date').strip()
            source = getSource(imagepage, source=convertLinks(match.group(u'source').strip(), imagepage.site()))
            author = convertLinks(match.group(u'author').strip(), imagepage.site())
            if u'permission' in match.groupdict():
                permission = convertLinks(match.group(u'permission').strip(), imagepage.site())
            if  u'other_versions' in match.groupdict():
                other_versions = convertLinks(match.group(u'other_versions').strip(), imagepage.site())
            # Return the stuff we found
            return (description, date, source, author)
    
    #We didn't find anything, return the empty strings
    return (description, date, source, author)

def getNewFieldsFromFreetext(imagepage):
    '''
    '''
    text = imagepage.get()
    #text = re.sub(u'== Summary ==', u'', text, re.IGNORECASE)
    #text = re.sub(u'== Licensing ==', u'', text, re.IGNORECASE)
    #text = re.sub(u'\{\{(self|self2)\|[^\}]+\}\}', u'', text, re.IGNORECASE)

    for toRemove in sourceGarbage:
        text = re.sub(toRemove, u'', text, re.IGNORECASE)
    
    for (regex, repl) in licenseTemplates:
        text = re.sub(regex, u'', text, re.IGNORECASE)

    text = wikipedia.removeCategoryLinks(text, imagepage.site()).strip()
        
    description = convertLinks(text.strip(), imagepage.site())
    date = getUploadDate(imagepage)
    source = getSource(imagepage)
    author = getAuthorText(imagepage)
    return (description, date, source, author)

def getUploadDate(imagepage):
    # Get the original upload date
    uploadtime = imagepage.getFileVersionHistory()[-1][0]
    uploadDatetime = datetime.strptime(uploadtime, u'%Y-%m-%dT%H:%M:%SZ')
    return u'{{Date|' + str(uploadDatetime.year) + u'|' + str(uploadDatetime.month) + u'|' + str(uploadDatetime.day) + u'}} (original upload date)'

def getSource(imagepage, source=u''):
    site = imagepage.site()
    lang = site.language()
    family = site.family.name
    if source==u'':
        source=u'{{Own}}'
        
    return source.strip() + u'<BR />Transferred from [http://%(lang)s.%(family)s.org %(lang)s.%(family)s]' % {u'lang' : lang, u'family' : family}

def getAuthorText(imagepage):
    site = imagepage.site()
    lang = site.language()
    family = site.family.name
    
    firstuploader = getAuthor(imagepage)
    #FIXME : Make other sites than Wikipedia work
    return u'[[:%(lang)s:User:%(firstuploader)s|%(firstuploader)s]] at [http://%(lang)s.%(family)s.org %(lang)s.%(family)s]' % {u'lang' : lang, u'family' : family , u'firstuploader' : firstuploader}

def getAuthor(imagepage):
    return imagepage.getFileVersionHistory()[-1][1].strip()

def convertLinks(text, sourceSite):
    lang = sourceSite.language()
    family = sourceSite.family.name
    conversions =[(u'\[\[([^\[\]\|]+)\|([^\[\]\|]+)\]\]', u'[[:%(lang)s:\\1|\\2]]'),
                  (u'\[\[([^\[\]\|]+)\]\]', u'[[:%(lang)s:\\1|\\1]]'),
                  ]
    
    for (regex, replacement) in conversions:
        text = re.sub(regex, replacement, text)              

    return text % {u'lang' : lang, u'family' : family}

def getNewLicensetemplate(imagepage):
    '''
    '''
    text = imagepage.get()
    
    site = imagepage.site()
    lang = site.language()
    family = site.family.name

    result = u''   

    for (regex, replacement) in licenseTemplates:
        match = re.search(regex, text, re.IGNORECASE)
        if match:
            result = re.sub(regex, replacement, match.group(0), re.IGNORECASE)
            return result % {u'author' : getAuthor(imagepage),
                             u'lang' : lang,
                             u'family' : family}
        
    return result
    
def getNewCategories(imagepage):
    '''
    Get a categories for the image
    Dont forget to filter
    '''
    result = u''
    (commonshelperCats, usage, galleries) = imagerecat.getCommonshelperCats(imagepage)
    newcats = imagerecat.applyAllFilters(commonshelperCats)
    for newcat in newcats:
        result = result + u'[[Category:' + newcat + u']] '
    return result

def getOriginalUploadLog(imagepage):
    filehistory = imagepage.getFileVersionHistory()
    filehistory.reverse()

    site = imagepage.site()
    lang = site.language()
    family = site.family.name

    sourceimage = imagepage.site().get_address(imagepage.title()).replace(u'&redirect=no&useskin=monobook', u'')
    
    result = u'== {{Original upload log}} ==\n'
    result = result + u'The original description page is/was [http://%(lang)s.%(family)s.org%(sourceimage)s here]. All following user names refer to %(lang)s.%(family)s.\n' % {u'lang' : lang, u'family' : family , u'sourceimage' : sourceimage}
    for (timestamp, username, resolution, size, comment) in filehistory:
        date = datetime.strptime(timestamp, u'%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M')
        result = result + u'* %(date)s [[:%(lang)s:user:%(username)s|%(username)s]] %(resolution)s (%(size)s bytes) \'\'<nowiki>%(comment)s</nowiki>\'\'\n' % {
            u'lang' : lang,
            u'family' : family ,
            u'date' : date,
            u'username' : username,
            u'resolution': resolution,
            u'size': size,
            u'comment' : comment}       
        
    return result

    

def buildNewImageDescription(imagepage, description, date, source, author, licensetemplate, categories, checkTemplate):
    '''
    Build a new information template 
    '''
    
    site = imagepage.site()
    lang = site.language()
    family = site.family.name
    
    cid = u''
    if checkTemplate:
        cid = cid + u'\n{{BotMoveToCommons|%(lang)s.%(family)s|year={{subst:CURRENTYEAR}}|month={{subst:CURRENTMONTHNAME}}|day={{subst:CURRENTDAY}}}}\n' % {u'lang' : lang, u'family' : family}
    cid = cid + u'== {{int:filedesc}} ==\n'
    cid = cid + u'{{Information\n'
    cid = cid + u'|description={{%(lang)s|1=' % {u'lang' : lang, u'family' : family}
    cid = cid + description + u'}}\n' 
    cid = cid + u'|date=' + date + u'\n'
    cid = cid + u'|source=' + source + u'\n'
    cid = cid + u'|author=' + author + u'\n'
    cid = cid + u'|permission=\n'
    cid = cid + u'|other_versions=\n'
    cid = cid + u'}}\n'
    cid = cid + u'== {{int:license}} ==\n'
    cid = cid + licensetemplate + u'\n'
    cid = cid + u'\n'
    cid = cid + getOriginalUploadLog(imagepage)
    cid = cid + u'__NOTOC__\n'
    if categories.strip()==u'':
        cid = cid + u'{{Subst:Unc}}'
    else:
        cid = cid + categories
    return cid


def processImage(page, checkTemplate):
    skip = False
    if page.exists() and (page.namespace() == 6) and (not page.isRedirectPage()):
        imagepage = wikipedia.ImagePage(page.site(), page.title())

        #First do autoskip.
        if doiskip(imagepage):
            wikipedia.output("Skipping " + page.title())
            skip = True
        else:
            currentcontent = getNewFields(imagepage)

            while True:
                # Do the Tkdialog to accept/reject and change te name
                (filename, description, date, source, author, licensetemplate, categories, skip)=Tkdialog(imagepage, currentcontent).getnewmetadata()

                if skip:
                    wikipedia.output('Skipping this image')
                    break
                       
                # Check if the image already exists
                CommonsPage=wikipedia.Page(wikipedia.getSite('commons', 'commons'), u'File:' + filename)
                if not CommonsPage.exists():
                    break
                else:
                    wikipedia.output('Image already exists, pick another name or skip this image')
                    # We dont overwrite images, pick another name, go to the start of the loop   
            
            if not skip:
                cid = buildNewImageDescription(imagepage, description, date, source, author, licensetemplate, categories, checkTemplate)
                wikipedia.output(cid)
                bot = UploadRobot(url=imagepage.fileUrl(), description=cid, useFilename=filename, keepFilename=True, verifyDescription=False, ignoreWarning = True, targetSite = wikipedia.getSite('commons', 'commons'))
                bot.run()
                
                if wikipedia.Page(wikipedia.getSite('commons', 'commons'), u'File:' + filename).exists():
                    #Get a fresh copy, force to get the page so we dont run into edit conflicts
                    imtxt=imagepage.get(force=True)

                    #Remove the move to commons templates
                    if imagepage.site().language() in moveToCommonsTemplate:
                        for moveTemplate in moveToCommonsTemplate[imagepage.site().language()]:
                            imtxt = re.sub(u'(?i)\{\{' + moveTemplate + u'[^\}]*\}\}', u'', imtxt)

                    #add {{NowCommons}}
                    if imagepage.site().language() in nowCommonsTemplate:
                        addTemplate = nowCommonsTemplate[imagepage.site().language()] % filename
                    else:
                        addTemplate = nowCommonsTemplate['_default'] % filename

                    if imagepage.site().language() in nowCommonsMessage:
                        commentText = nowCommonsMessage[imagepage.site().language()]
                    else:
                        commentText = nowCommonsMessage['_default']

                    wikipedia.showDiff(imagepage.get(), imtxt + addTemplate)
                    imagepage.put(imtxt + addTemplate, comment = commentText)

                    gen = pagegenerators.FileLinksGenerator(imagepage)
                    preloadingGen = pagegenerators.PreloadingGenerator(gen)

                    #If the image is uploaded under a different name, replace all instances
                    if imagepage.titleWithoutNamespace() != filename:
                        if imagepage.site().language() in imageMoveMessage:
                            moveSummary = imageMoveMessage[imagepage.site().language()] % (imagepage.titleWithoutNamespace(), filename)
                        else:
                            moveSummary = imageMoveMessage['_default'] % (imagepage.titleWithoutNamespace(), filename)
                        imagebot = ImageRobot(generator = preloadingGen, oldImage = imagepage.titleWithoutNamespace(), newImage = filename, summary = moveSummary, always = True, loose = True)
                        imagebot.run()             
    


def main(args):
    generator = None;
    #newname = "";
    imagepage = None;
    always = False
    checkTemplate = True
    imagerecat.initLists()
    # Load a lot of default generators
    genFactory = pagegenerators.GeneratorFactory()

    for arg in wikipedia.handleArgs():
        if arg == '-nochecktemplate':
            checkTemplate = False
        else:
            genFactory.handleArg(arg)
    
    generator = genFactory.getCombinedGenerator()
    if not generator:
        raise add_text.NoEnoughData('You have to specify the generator you want to use for the script!')

    pregenerator = pagegenerators.PreloadingGenerator(generator)

    for page in pregenerator:
        processImage(page, checkTemplate)


    wikipedia.output(u'Still ' + str(threading.activeCount()) + u' active threads, lets wait')
    for openthread in threading.enumerate():
        if openthread != threading.currentThread():
            openthread.join()
    wikipedia.output(u'All threads are done')

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        wikipedia.stopme()