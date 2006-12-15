# -*- coding: utf-8 -*-
"""
This bot makes the cleaned of the page of tests.

Syntax:
6 hours: clean_sandbox.py -hours:6
1 second: clean_sandbox.py -hours:0.001

"""
import wikipedia
import time

content = {
    'de': u'{{Bitte erst NACH dieser Zeile schreiben! (Begrüßungskasten)}}\r\n',
    'en': u'{{Please leave this line alone (sandbox heading)}}\n <!-- Hello! Feel free to try your formatting and editing skills below this line. As this page is for editing experiments, this page will automatically be cleaned every 12 hours. -->',
    'pt': u'<!--não apague esta linha-->{{página de testes}}<!--não apagar-->\r\n',
    }

msg = {
    'de': u'Bot: Setze Seite zurück.',
    'en': u'Robot: This page will automatically be cleaned.',
    'pt': u'Bot: Limpeza da página de testes',
    }
    
sandboxTitle = {
    'de': u'Wikipedia:Spielwiese',
    'en': u'Wikipedia:Sandbox',
    'pt': u'Wikipedia:Página de testes',
    }

class SandboxBot:
    def __init__(self, hours):
        self.hours = hours
    
    def run(self):
        mySite = wikipedia.getSite()
        while True:
            now = time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
            localSandboxTitle = wikipedia.translate(mySite, sandboxTitle)
            sandboxPage = wikipedia.Page(mySite, localSandboxTitle)
            try:
                text = sandboxPage.get()
                translatedContent = wikipedia.translate(mySite, content)
                if text.strip() == translatedContent.strip():
                    wikipedia.output(u'The sandbox is still clean, no change necessary.')
                else:
                    translatedMsg = wikipedia.translate(mySite, msg)
                    sandboxPage.put(translatedContent, translatedMsg)
            except wikipedia.EditConflict:
                wikipedia.output(u'*** Loading again because of edit conflict.\n')
            wikipedia.output(u'\nSleeping %s hours, now %s' % (self.hours, now))
            time.sleep(self.hours * 60 * 60)

def main():
    for arg in wikipedia.handleArgs():
        if arg.startswith('-hours:'):
            hours = float(arg[7:])
        else:
            wikipedia.showHelp('clean_sandbox')

        if hours:
            bot = SandboxBot(hours)
            bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
