//
//  PythonProcessManager.swift
//  ClipboardMonitor
//
//  Created by flybywind wen on 2024/10/17.
//

import Foundation
import os

class PythonProcessManager {
    private let pythonScript: String
    private let pythonProcess = Process()
    private let inputPipe = Pipe()
    private let outputPipe = Pipe()
    private var outputHandler: ((String) -> Void)?
    
    private let logger = Logger(subsystem: "wtx.ClipboardMonitor", category: "PythonProcessManager")
    
    init(scriptPath: String) {
        self.pythonScript = scriptPath
        setupPythonProcess()
    }
    
    private func setupPythonProcess() {
        pythonProcess.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        pythonProcess.arguments = ["-u", pythonScript]
        pythonProcess.standardInput = inputPipe
        pythonProcess.standardOutput = outputPipe
        
        outputPipe.fileHandleForReading.readabilityHandler = { [weak self] fileHandle in
            guard let self = self else { return }
            let data = fileHandle.availableData
            if let output = String(data: data, encoding: .utf8) {
                self.logger.debug("Python output: \(output)")
            }
        }
    }
    
    func start() throws {
        try pythonProcess.run()
        logger.info("\(self.pythonScript) process started")
    }
    
    func stop() {
        pythonProcess.terminate()
        logger.info("Python process terminated")
    }
    
    func send(_ content: String) {
        inputPipe.fileHandleForWriting.write((content + "\n").data(using: .utf8)!)
    }
}


