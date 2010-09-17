from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

from backend import *


class FirewallPlugin(CategoryPlugin):
    text = 'Firewall'
    icon = '/dl/firewall/icon_small.png'
    folder = 'system'

    def on_init(self):
        self.cfg = Config()
        self.cfg.load()

    def on_session_start(self):
        self._tab = 0
        self._shuffling = None
        self._shuffling_table = None
        self._adding_chain = None
        
    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(), title='IPTables Firewall', icon='/dl/firewall/icon.png')
        panel.append(self.get_default_ui())
        return panel

    def get_default_ui(self):
        tc = UI.TabControl(active=self._tab)
        for t in self.cfg.tables:
            t = self.cfg.tables[t]
            vc = UI.VContainer(spacing=15)
            for ch in t.chains:
                ch = t.chains[ch]
                uic = UI.FWChain(tname=t.name, name=ch.name, default=ch.default)
                for r in ch.rules:
                    uic.append(UI.FWRule(action=r.action, desc=r.raw))
                vc.append(uic)
            vc.append(UI.Button(text='Add new chain to '+t.name, id='addchain/'+t.name))
            tc.add(t.name, vc)
            
        ui = UI.VContainer(
                UI.Label(size=3, text='Rule tables'),
                tc
             )
             
        if self._shuffling != None:
            ui.append(self.get_ui_shuffler())
      
        if self._adding_chain != None:
            ui.append(UI.InputBox(id='dlgAddChain', text='Chain name:'))

        return ui

    def get_ui_shuffler(self):
        li = UI.SortList(id='list')
        for r in self.cfg.tables[self._shuffling_table].chains[self._shuffling].rules:
            li.append(
                UI.SortListItem(
                    UI.FWRule(action=r.action, desc=r.raw), id=r.raw
                ))

        return UI.DialogBox(li, id='dlgShuffler')
               
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'setdefault':
            self._tab = self.cfg.table_index(params[1])
            self.cfg.tables[params[1]].chains[params[2]].default = params[3]
            self.cfg.save()
        if params[0] == 'shuffle':
            self._tab = self.cfg.table_index(params[1])
            self._shuffling_table = params[1]
            self._shuffling = params[2]
        if params[0] == 'addchain':
            self._tab = self.cfg.table_index(params[1])
            self._adding_chain = params[1]
        if params[0] == 'deletechain':
            self._tab = self.cfg.table_index(params[1])
            self.cfg.tables[params[1]].chains.pop(params[2])
            self.cfg.save()
            
    @event('dialog/submit')
    def on_submit(self, event, params, vars):
        if params[0] == 'dlgAddChain':
            if vars.getvalue('action', '') == 'OK':
                n = vars.getvalue('value', '')
                if n == '': return
                self.cfg.tables[self._adding_chain].chains[n] = Chain(n, '-')
                self.cfg.save()
            self._adding_chain = None
        if params[0] == 'dlgShuffler':
            if vars.getvalue('action', '') == 'OK':
                d = vars.getvalue('list', '').split('|')
                ch = self.cfg.tables[self._shuffling_table].chains[self._shuffling]
                ch.rules = []
                for s in d:
                    ch.rules.append(Rule(s))
                self.cfg.save()
            self._shuffling = None
            self._shuffling_table = None
class FirewallContent(ModuleContent):
    module = 'firewall'
    path = __file__
    widget_files = ['fw.xslt']
    css_files = ['fw.css']
