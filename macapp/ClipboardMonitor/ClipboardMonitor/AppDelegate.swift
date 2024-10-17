//
//  AppDelegate.swift
//  ClipboardMonitor
//
//  Created by flybywind wen on 2024/10/16.
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

    override init() {
        lastClipboardContent = ""
        pythonProcess = Process()
        pythonInput = Pipe()
        pythonOutput = Pipe()
        
        super.init()
        
        // Set up Python process
        pythonProcess.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        pythonProcess.arguments = ["/Users/flybywindwen/Projects/llm-wechat/echo.py"]
        pythonProcess.standardInput = pythonInput.fileHandleForWriting
        pythonProcess.standardOutput = pythonOutput.fileHandleForReading
        
        do {
            try pythonProcess.run()
        } catch {
            logger.error("Failed to start Python process: \(error)")
        }
        // Set up asynchronous reading from Python output
        pythonOutput.fileHandleForReading.readabilityHandler = { fileHandle in
            do {
                let data = try fileHandle.readToEnd()!
                if let output = String(data: data, encoding: .utf8), !output.isEmpty {
                    self.logger.info("Python output: \(output)")
                    // Here you can process the output as needed
                }
            } catch {
                self.logger.error("failed to read output of python: \(error)")
            }
        
        }
    }
    deinit {
        // Clean up
        pythonOutput.fileHandleForReading.readabilityHandler = nil
        pythonProcess.terminate()
    }

    func applicationDidFinishLaunching(_ aNotification: Notification) {
        
        if let button = statusItem.button {
            button.image = NSImage(named: NSImage.Name("StatusBarButtonImage"))
        }
        
        // Start monitoring clipboard
//        Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
//            self.checkClipboard()
//        }
        startKeyboardMonitoring()
    }
    
    func startKeyboardMonitoring() {
        keyboardMonitor = NSEvent.addGlobalMonitorForEvents(matching: [.keyUp]) { (event) in
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
                // You can add your custom logic here
            }
        }
    }
    func checkClipboard() {
        if let content = pasteboard.string(forType: .string) {
            if !content.isEmpty && !content.elementsEqual(lastClipboardContent) {
                sendToPython(content:content)
            }
        }
    }

    func sendToPython(content: String) {
        logger.debug("send data: \(content)")
        
        if let data = content.data(using: .utf8) {
            pythonInput.fileHandleForWriting.write(data)
        }
    }
}

