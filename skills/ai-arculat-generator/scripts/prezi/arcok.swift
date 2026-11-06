// Arcok a macOS Vision keretrendszerrel, a fejet nem vágó képkivágáshoz (opcionális; máshol OpenCV vagy fókuszpont).
// Használat: swift arcok.swift kep1.jpg kep2.png ...
// Kimenet: JSON {"kep": [[x0,y0,x1,y1], ...]}, 0..1 tartományban, bal FELSŐ sarok az origó.
import Foundation
import Vision
import AppKit

var out: [String: [[Double]]] = [:]
func box(_ b: CGRect) -> [Double] { [Double(b.minX), Double(1 - b.maxY), Double(b.maxX), Double(1 - b.minY)] }
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { out[path] = []; continue }
    let f = VNDetectFaceRectanglesRequest()
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([f])
    out[path] = (f.results ?? []).filter { $0.confidence > 0.6 }.map { box($0.boundingBox) }
}
print(String(data: try! JSONSerialization.data(withJSONObject: out), encoding: .utf8)!)
