"""Dedicated GTK/WebKit offline Find Eden window; never opens Firefox."""
from pathlib import Path
import sys
from urllib.parse import urldefrag
from .find_eden_assets import default_pack

def navigation_allowed(uri, page):
    return isinstance(uri,str) and urldefrag(uri)[0] == page

def main():
    import gi
    gi.require_version('Gtk','4.0')
    gi.require_version('WebKit','6.0')
    from gi.repository import Gio, Gtk, WebKit
    page=(default_pack()/'Find-Eden.html').resolve().as_uri()

    class FindEdenApplication(Gtk.Application):
        def __init__(self):
            super().__init__(application_id='uk.edenos.FindEden',flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        def do_activate(self):
            if self.props.active_window:
                self.props.active_window.present();return
            window=Gtk.ApplicationWindow(application=self,title='Find Eden!')
            window.set_default_size(1100,850)
            header=Gtk.HeaderBar()
            back=Gtk.Button(label='Back to Eden')
            back.connect('clicked',lambda _button:window.close())
            header.pack_start(back);window.set_titlebar(header)
            view=WebKit.WebView(network_session=WebKit.NetworkSession.new_ephemeral())
            settings=view.get_settings()
            settings.set_enable_developer_extras(False)
            settings.set_enable_html5_local_storage(False)
            settings.set_javascript_can_open_windows_automatically(False)
            def policy(_view,decision,kind):
                if kind==WebKit.PolicyDecisionType.NAVIGATION_ACTION:
                    uri=decision.get_navigation_action().get_request().get_uri()
                    decision.use() if navigation_allowed(uri,page) else decision.ignore()
                    return True
                if kind==WebKit.PolicyDecisionType.NEW_WINDOW_ACTION:
                    decision.ignore();return True
                return False
            def loaded(_view,event):
                if event==WebKit.LoadEvent.FINISHED:
                    view.evaluate_javascript("document.getElementById('today').click()",-1,None,None,None,None,None)
            view.connect('decide-policy',policy)
            view.connect('load-changed',loaded)
            view.connect('context-menu',lambda *_args:True)
            window.set_child(view);view.load_uri(page);window.present()

    return FindEdenApplication().run(sys.argv)

if __name__=='__main__':raise SystemExit(main())
