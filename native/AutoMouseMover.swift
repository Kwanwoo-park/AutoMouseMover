import AppKit
import ApplicationServices

@MainActor
final class AppDelegate: NSObject, NSApplicationDelegate {
    private let interval: TimeInterval = 30
    private var window: NSWindow!
    private var timer: Timer?
    private var statusLabel: NSTextField!
    private var pauseButton: NSButton!

    func applicationDidFinishLaunching(_ notification: Notification) {
        buildMenu()
        buildWindow()
        requestAccessibilityPermission()
        startTimer()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }

    private func buildMenu() {
        let mainMenu = NSMenu()
        let appMenuItem = NSMenuItem()
        let appMenu = NSMenu()
        appMenu.addItem(
            withTitle: "AutoMouseMover 종료",
            action: #selector(NSApplication.terminate(_:)),
            keyEquivalent: "q"
        )
        appMenuItem.submenu = appMenu
        mainMenu.addItem(appMenuItem)
        NSApp.mainMenu = mainMenu
    }

    private func buildWindow() {
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 420, height: 220),
            styleMask: [.titled, .closable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        window.title = "AutoMouseMover"
        window.center()

        let titleLabel = NSTextField(labelWithString: "화면 보호기 방지")
        titleLabel.font = .systemFont(ofSize: 22, weight: .semibold)
        titleLabel.alignment = .center

        statusLabel = NSTextField(labelWithString: "")
        statusLabel.font = .systemFont(ofSize: 14)
        statusLabel.textColor = .secondaryLabelColor
        statusLabel.alignment = .center
        statusLabel.maximumNumberOfLines = 2

        pauseButton = makeButton(title: "일시 중지", action: #selector(pause))
        let restartButton = makeButton(title: "재시작", action: #selector(restart))
        restartButton.keyEquivalent = "\r"
        let quitButton = makeButton(title: "종료", action: #selector(quit))

        let buttonStack = NSStackView(views: [pauseButton, restartButton, quitButton])
        buttonStack.orientation = .horizontal
        buttonStack.spacing = 12
        buttonStack.distribution = .fillEqually

        let stack = NSStackView(views: [titleLabel, statusLabel, buttonStack])
        stack.orientation = .vertical
        stack.spacing = 22
        stack.edgeInsets = NSEdgeInsets(top: 24, left: 28, bottom: 24, right: 28)
        stack.translatesAutoresizingMaskIntoConstraints = false

        guard let contentView = window.contentView else { return }
        contentView.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            stack.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),
            stack.topAnchor.constraint(equalTo: contentView.topAnchor),
            stack.bottomAnchor.constraint(equalTo: contentView.bottomAnchor),
            buttonStack.heightAnchor.constraint(equalToConstant: 36),
        ])
    }

    private func makeButton(title: String, action: Selector) -> NSButton {
        let button = NSButton(title: title, target: self, action: action)
        button.bezelStyle = .rounded
        button.font = .systemFont(ofSize: 14, weight: .medium)
        return button
    }

    private func requestAccessibilityPermission() {
        let key = kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String
        let options = [key: true] as CFDictionary
        _ = AXIsProcessTrustedWithOptions(options)
    }

    private func startTimer() {
        timer?.invalidate()
        timer = Timer.scheduledTimer(
            timeInterval: interval,
            target: self,
            selector: #selector(nudgeCursor),
            userInfo: nil,
            repeats: true
        )
        pauseButton.isEnabled = true
        updateRunningStatus()
    }

    private func updateRunningStatus() {
        if AXIsProcessTrusted() {
            statusLabel.stringValue = "실행 중 • 30초마다 커서를 움직입니다."
            statusLabel.textColor = .systemGreen
        } else {
            statusLabel.stringValue = "손쉬운 사용 권한을 허용해 주세요.\n허용 후 ‘재시작’을 누르세요."
            statusLabel.textColor = .systemOrange
        }
    }

    @objc private func nudgeCursor() {
        guard AXIsProcessTrusted(), let currentEvent = CGEvent(source: nil) else {
            updateRunningStatus()
            return
        }

        let original = currentEvent.location
        let offset: CGFloat = original.x >= 1 ? -1 : 1
        let moved = CGPoint(x: original.x + offset, y: original.y)
        postMouseMove(to: moved)

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) { [weak self] in
            self?.postMouseMove(to: original)
        }
    }

    private func postMouseMove(to point: CGPoint) {
        CGEvent(
            mouseEventSource: nil,
            mouseType: .mouseMoved,
            mouseCursorPosition: point,
            mouseButton: .left
        )?.post(tap: .cghidEventTap)
    }

    @objc private func pause() {
        timer?.invalidate()
        timer = nil
        statusLabel.stringValue = "일시 중지됨"
        statusLabel.textColor = .secondaryLabelColor
        pauseButton.isEnabled = false
    }

    @objc private func restart() {
        nudgeCursor()
        startTimer()
    }

    @objc private func quit() {
        timer?.invalidate()
        NSApp.terminate(nil)
    }
}

@main
struct AutoMouseMoverApp {
    @MainActor
    static func main() {
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.setActivationPolicy(.regular)
        app.run()
    }
}
