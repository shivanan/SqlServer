import sublime,sublime_plugin
import os,re,sys
import subprocess
import functools
import thread
def updir(x):
    return os.path.dirname(x)

SETTINGS_FILE = 'sql-server.sublime-settings'
def load_settings():
    return sublime.load_settings(SETTINGS_FILE)

def ask_for_account(window,cb=None):
    if not cb: cb = lambda x:x
    settings = load_settings()
    lst = settings.get('dblist')
    if not lst: lst = []

    def selected_account(ind):
        if ind < 0: return
        if ind > 0:
            account = lst[ind-1]
            settings.set('currentdb',account)
            sublime.save_settings(SETTINGS_FILE)
            cb(account)
            return
        else:
            def savenewaccount(txt):
                if not txt: return
                if not txt in lst: lst.append(txt)
                settings.set('currentdb',txt)
                settings.set('dblist',lst)
                sublime.save_settings(SETTINGS_FILE)
                cb(txt)
            window.show_input_panel('New DB Connection','user id=abc;pwd=ssssh;data source=.\\sqlexpress;initial catalog=dbname',savenewaccount,None,None)
    
    window.show_quick_panel(['New DB Connection'] + mapcslist(lst),selected_account)

def get_account(window,cb):
    settings = load_settings()
    account = settings.get('currentdb')
    if account:
        cb(account)
        return
    ask_for_account(window,cb)

def sql_exec(window,cs,command,show_console=True):
    
    def print_output_panel(lines):
        def main_thread_show():
            message = ''.join(lines).replace('\r','')
            v = window.get_output_panel("sqlserver")
            window.run_command("show_panel",{"panel":"output.sqlserver"})
            v.set_read_only(False)
            edit = v.begin_edit()
            v.erase(edit, sublime.Region(0, v.size()))
            v.insert(edit, v.size(), message)
            v.end_edit(edit)
            v.set_read_only(True)
        
        sublime.set_timeout(main_thread_show,0)
    
    startupinfo = subprocess.STARTUPINFO()
    if not show_console:
        if os.name == 'nt': startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
   
    csx = parse_cs(cs)
    sql_command ='osql -w 10000 -S ' + csx['data source'] + ' -U ' + csx['user id'] + ' -P ' + csx['pwd'] + ' -d ' + csx['initial catalog']
    p = subprocess.Popen(sql_command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE,startupinfo=startupinfo)
    def show_output():
        p.stdin.write(command)
        output,err = p.communicate()
        if not err: err = ''
        p.stdin.close()
        p.wait()
        header = ['Result from ' + sql_command]
        print_output_panel(header + [err] + [output])

    thread.start_new_thread(show_output,())
    v = window.get_output_panel("sqlserver")
    window.run_command("show_panel",{"panel":"output.sqlserver"})
    v.set_read_only(False)
    edit = v.begin_edit()
    v.erase(edit, sublime.Region(0, v.size()))
    v.insert(edit, v.size(), ''.join(['Running ' + sql_command]))
    v.end_edit(edit)
    v.set_read_only(True)
        

def runsql(window,command,show_console=True):
    def doit(account):
        sql_exec(window,account,command,show_console)
    get_account(window,doit)

def parse_cs(x):
    r = {}
    parts = x.split(';')
    for part in parts:
        kvp = part.split('=',1)
        if len(kvp) != 2: continue
        r[kvp[0].strip()] = kvp[1].strip()
    for d in ['initial catalog','data source','user id','pwd']:
        if not d in r: d[r] = ''
    return r



def mapcslist(lst):
    def fmt(x):
        r = parse_cs(x)
        return 'server:' + r.get('data source','not set') + \
        ' ' + 'database:' + r.get('initial catalog','not set')
    return map(fmt,lst)
class SetConnectionString(sublime_plugin.WindowCommand):
    def run(self):
        ask_for_account(self.window)
class DeleteConnectionString(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        settings = load_settings()
        lst = settings.get('dblist')
        if not lst: lst = ['Nothing to delete']
        def selected_account(i):
            x = lst[i]
            if x == 'Nothing to delete': return
            del lst[i]
            settings.set('dblist',lst)
            if settings.get('currentdb') == x:
                settings.set('currentdb','')
            sublime.save_settings(SETTINGS_FILE)
        window.show_quick_panel(mapcslist(lst),selected_account)

class ExecuteSql(sublime_plugin.TextCommand):
    def run(self,view):
        view = self.view
        window = self.view.window()
        sql = view.substr(view.sel()[0])
        if not sql:
            sql = view.substr(sublime.Region(0, view.size()))
        runsql(window,sql)

