import Foundation
import Vision
import AppKit

struct OCRLine: Codable {
    let text: String
    let minX: Double
    let minY: Double
}

func loadImage(at path: String) -> CGImage? {
    guard let image = NSImage(contentsOfFile: path) else { return nil }
    var rect = CGRect(origin: .zero, size: image.size)
    return image.cgImage(forProposedRect: &rect, context: nil, hints: nil)
}

guard CommandLine.arguments.count >= 2 else {
    fputs("usage: swift ocr_progress_chart.swift <image-path>\n", stderr)
    exit(1)
}

let imagePath = CommandLine.arguments[1]
guard let cgImage = loadImage(at: imagePath) else {
    fputs("failed to load image: \(imagePath)\n", stderr)
    exit(1)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = ["ko-KR", "en-US"]
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
} catch {
    fputs("vision request failed: \(error)\n", stderr)
    exit(1)
}

let observations = request.results as? [VNRecognizedTextObservation] ?? []
let lines = observations.compactMap { observation -> OCRLine? in
    guard let candidate = observation.topCandidates(1).first else { return nil }
    let text = candidate.string.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !text.isEmpty else { return nil }
    let box = observation.boundingBox
    return OCRLine(text: text, minX: box.minX, minY: box.minY)
}

let sorted = lines.sorted {
    if abs($0.minY - $1.minY) > 0.015 {
        return $0.minY > $1.minY
    }
    return $0.minX < $1.minX
}

let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
do {
    let data = try encoder.encode(sorted)
    FileHandle.standardOutput.write(data)
} catch {
    fputs("failed to encode json: \(error)\n", stderr)
    exit(1)
}
