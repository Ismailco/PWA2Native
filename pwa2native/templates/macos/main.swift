import Cocoa
import WebKit

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    var shortcutURLs: [String: String] = [:]
    var navigationMenu: NSMenu?

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Create the main menu
        setupMenu()

        // Setup window
        let windowRect = NSRect(x: 0, y: 0, width: 1024, height: 768)
        window = NSWindow(
            contentRect: windowRect,
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )

        window.title = "${app_name}"
        window.center()

        // Setup WebView with navigation
        let config = WKWebViewConfiguration()
        webView = WKWebView(frame: window.contentView!.bounds, configuration: config)
        webView.navigationDelegate = self
        webView.allowsBackForwardNavigationGestures = true
        webView.autoresizingMask = [.width, .height]

        if let url = URL(string: "${url}") {
            webView.load(URLRequest(url: url))
        }

        window.contentView?.addSubview(webView)
        window.makeKeyAndOrderFront(nil)
    }

    func setupMenu() {
        let mainMenu = NSMenu()

        // App menu
        let appMenuItem = NSMenuItem()
        let appMenu = NSMenu()
        appMenuItem.submenu = appMenu

        let aboutItem = NSMenuItem(
            title: "About ${app_name}",
            action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)),
            keyEquivalent: ""
        )
        appMenu.addItem(aboutItem)
        appMenu.addItem(NSMenuItem.separator())

        let quitItem = NSMenuItem(
            title: "Quit ${app_name}",
            action: #selector(NSApplication.terminate(_:)),
            keyEquivalent: "q"
        )
        appMenu.addItem(quitItem)
        mainMenu.addItem(appMenuItem)

        // Navigation menu with website links
        let navigationMenuItem = NSMenuItem()
        let navigationMenu = NSMenu(title: "Navigation")
        navigationMenuItem.submenu = navigationMenu

        // Standard navigation items
        let backItem = NSMenuItem(
            title: "Back",
            action: #selector(navigateBack(_:)),
            keyEquivalent: "["
        )
        backItem.keyEquivalentModifierMask = .command
        navigationMenu.addItem(backItem)

        let forwardItem = NSMenuItem(
            title: "Forward",
            action: #selector(navigateForward(_:)),
            keyEquivalent: "]"
        )
        forwardItem.keyEquivalentModifierMask = .command
        navigationMenu.addItem(forwardItem)

        let reloadItem = NSMenuItem(
            title: "Reload",
            action: #selector(reloadPage(_:)),
            keyEquivalent: "r"
        )
        navigationMenu.addItem(reloadItem)
        navigationMenu.addItem(NSMenuItem.separator())

        // Website navigation links
        ${navigation_links}

        mainMenu.addItem(navigationMenuItem)

        // Shortcuts menu
        ${shortcuts_menu}

        NSApplication.shared.mainMenu = mainMenu
    }

    @objc func navigateBack(_ sender: Any?) {
        if webView.canGoBack {
            webView.goBack()
        }
    }

    @objc func navigateForward(_ sender: Any?) {
        if webView.canGoForward {
            webView.goForward()
        }
    }

    @objc func reloadPage(_ sender: Any?) {
        webView.reload()
    }

    @objc func loadURL(_ sender: NSMenuItem) {
        if let urlString = shortcutURLs[sender.title],
           let url = URL(string: urlString.hasPrefix("http") ? urlString : "${url}" + urlString) {
            webView.load(URLRequest(url: url))
        }
    }
}

extension AppDelegate: WKNavigationDelegate {
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        window.title = webView.title ?? "${app_name}"
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
