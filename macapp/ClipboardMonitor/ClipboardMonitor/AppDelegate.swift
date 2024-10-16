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
    var lastChangeCount: Int
    let pythonProcess: Process
    let pythonInput: Pipe
    let pythonOutput: Pipe

    let logger = Logger(subsystem: "wtx.ClipboardMonitor", category: "AppDelegate")

    override init() {
        lastChangeCount = pasteboard.changeCount
        pythonProcess = Process()
        pythonInput = Pipe()
        pythonOutput = Pipe()
        
        super.init()
        
        // Set up Python process
        pythonProcess.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        pythonProcess.arguments = ["/Users/flybywindwen/Projects/llm-wechat/echo.py"]
        pythonProcess.standardInput = pythonInput
        pythonProcess.standardOutput = pythonOutput
        
        do {
            try pythonProcess.run()
        } catch {
            logger.error("Failed to start Python process: \(error)")
        }
        // Set up asynchronous reading from Python output
        pythonOutput.fileHandleForReading.readabilityHandler = { fileHandle in
            let data = fileHandle.availableData
            if let output = String(data: data, encoding: .utf8) {
                logger.info("Python output: \(output)")
                // Here you can process the output as needed
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
        Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            self.checkClipboard()
        }
    }

    func checkClipboard() {
        if pasteboard.changeCount != lastChangeCount {
            lastChangeCount = pasteboard.changeCount
            if let items = pasteboard.pasteboardItems {
                for item in items {
                    if let str = item.string(forType: .string) {
                        sendToPython(content: str)
                    }
                }
            }
        }
    }

    func sendToPython(content: String) {
        if let data = (content + "\n").data(using: .utf8) {
            logger.debug("send data: " + )
            pythonInput.fileHandleForWriting.write(data)
        }
    }


}

