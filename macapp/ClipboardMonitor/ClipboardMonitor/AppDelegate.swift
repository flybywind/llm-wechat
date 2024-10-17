//
//  AppDelegate.swift
//  ClipboardMonitor
//
//  Created by flybywind wen on 2024/10/16.
// 注意，如果要获取keyboard事件，需要在 隐私与安全 --> 辅助功能 那边把这个app加进去
// ~/Library/Developer/Xcode/DerivedData/YourAppName-[random]/Build/Products/Debug/YourAppName.app
//

import Cocoa
import os
@main
class AppDelegate: NSObject, NSApplicationDelegate {
    let statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
    let pasteboard = NSPasteboard.general
    var lastClipboardContent: String
    var keyboardMonitor: Any?
    let pythonProcess: Process
    let pythonInput: Pipe
    let pythonOutput: Pipe

    let logger = Logger(subsystem: "wtx.ClipboardMonitor", category: "AppDelegate")
    let manager = PythonProcessManager(scriptPath: "/Users/flybywindwen/Projects/llm-wechat/echo.py")

    override init() {
        lastClipboardContent = ""
        pythonProcess = Process()
        pythonInput = Pipe()
        pythonOutput = Pipe()
        
        super.init()
        do {
            try manager.start()
        } catch {
            logger.error("start python manager failed \(error)")
        }

        manager.send("Hello, World!")
    }
    deinit {
        // When you're done
        manager.stop()
    }

    func applicationDidFinishLaunching(_ aNotification: Notification) {
        
        if let button = statusItem.button {
            button.image = NSImage(named: NSImage.Name("StatusBarButtonImage"))
        }
        
        startKeyboardMonitoring()
    }
    
    func startKeyboardMonitoring() {
        keyboardMonitor = NSEvent.addGlobalMonitorForEvents(matching: .keyUp) { (event) in
            self.handleKeyEvent(event)
        }
        logger.info("Keyboard monitoring started")
    }

    func handleKeyEvent(_ event: NSEvent) {
        // Here you can handle the keyboard event
        if event.modifierFlags.contains(.command) {
            let charOpt = event.charactersIgnoringModifiers
            if let char = charOpt, char.elementsEqual("c") {
                // 2 is the key code for 'C'
                logger.debug("'ctrl-c' key was pressed")
                checkClipboard()
                // You can add your custom logic here
            }
        }
    }
    func checkClipboard() {
        if let content = pasteboard.string(forType: .string) {
            if !content.isEmpty && !content.elementsEqual(lastClipboardContent) {
                logger.debug("send data: \(content)")
                manager.send(content)
                lastClipboardContent = content
            }
        }
    }
}

