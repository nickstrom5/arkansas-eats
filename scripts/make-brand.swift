// Arkansas Eats brand (final: Nick's decisions, 2026-11-07): the app icon is concept A of
// scripts/icon-concepts.swift, a bowl of cheese dip with a tortilla chip, on cardinal; the shared Eats Ranked icon style,
// state-prompts/ICON-STYLE.md, no backing shape. No school colours or marks (no hog, no "A"), no flag stars or text.
// Usage, from ar-eats/: swift scripts/make-brand.swift   -> ArkansasEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png,
// docs/ favicons and touch icons, docs/og.png. scripts/make-site.py draws the same mark as its inline SVG: change both together.
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
func R(_ s: CGFloat, _ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
    CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
}
func P(_ s: CGFloat, _ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: x * s, y: y * s) }
let CARDINAL: UInt32 = 0x9D2235, FOREST: UInt32 = 0x2E5E3E, LIME: UInt32 = 0xF3EEE3, GOLD: UInt32 = 0xE9C46A
let BOWL: UInt32 = 0xF7F3EA, BOWL2: UInt32 = 0xE2D9C6, QUESO: UInt32 = 0xF2B33D
let CHIP: UInt32 = 0xD9A441, CHIP2: UInt32 = 0xC08A2E

/// A: the cheese dip. Identical to icon-concepts.swift's concept A: a bowl seen from the side (a wide rounded trapezoid), queso mounded in it, a chip standing up out of the dip. CoreGraphics y-up.
func cheeseDip(_ c: CGContext, _ s: CGFloat) {
    c.saveGState(); defer { c.restoreGState() }
    c.translateBy(x: 0, y: 0.04 * s)   // centred (check.swift)
    // the chip: a tall triangle with rounded corners, behind the bowl's rim
    let chip = CGMutablePath()
    chip.move(to: P(s, 0.47, 0.50)); chip.addLine(to: P(s, 0.60, 0.74)); chip.addLine(to: P(s, 0.70, 0.50)); chip.closeSubpath()
    c.setLineJoin(.round); c.setLineWidth(0.05 * s)
    c.setFillColor(rgb(CHIP)); c.setStrokeColor(rgb(CHIP)); c.addPath(chip); c.drawPath(using: .fillStroke)
    let shade = CGMutablePath()
    shade.move(to: P(s, 0.60, 0.74)); shade.addLine(to: P(s, 0.70, 0.50)); shade.addLine(to: P(s, 0.63, 0.50)); shade.closeSubpath()
    c.setFillColor(rgb(CHIP2)); c.addPath(shade); c.fillPath()
    // the queso: a low dome over the rim
    c.setFillColor(rgb(QUESO)); c.fillEllipse(in: CGRect(x: 0.20 * s, y: 0.44 * s, width: 0.60 * s, height: 0.16 * s))
    // the bowl: wide at the rim, narrowing to a foot
    let bowl = CGMutablePath()
    bowl.move(to: P(s, 0.16, 0.52))
    bowl.addLine(to: P(s, 0.84, 0.52))
    bowl.addCurve(to: P(s, 0.62, 0.27), control1: P(s, 0.83, 0.40), control2: P(s, 0.74, 0.29))
    bowl.addLine(to: P(s, 0.38, 0.27))
    bowl.addCurve(to: P(s, 0.16, 0.52), control1: P(s, 0.26, 0.29), control2: P(s, 0.17, 0.40))
    bowl.closeSubpath()
    c.setFillColor(rgb(BOWL)); c.addPath(bowl); c.fillPath()
    c.setFillColor(rgb(BOWL2)); c.addPath(R(s, 0.16, 0.495, 0.68, 0.035, 0.0175)); c.fillPath()   // the rim's band
    c.setFillColor(rgb(BOWL)); c.addPath(R(s, 0.40, 0.22, 0.20, 0.06, 0.02)); c.fillPath()       // the foot
}

func render(_ n: Int, _ path: String, background: Bool) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: background ? CGImageAlphaInfo.noneSkipLast.rawValue : CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true)
    if background { ctx.setFillColor(rgb(CARDINAL)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n)) }
    cheeseDip(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
render(1024, "ArkansasEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", background: true)
try? FileManager.default.createDirectory(atPath: "docs", withIntermediateDirectories: true)
for (n, name) in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (32, "favicon-32.png")] {
    render(n, "docs/" + name, background: true)
}

/// The share image (1200 x 630): cardinal, the cheese dip at the left, the name in limestone and the tagline in diamond gold, and the
/// app's diamond band (Theme.swift's Stripes) along the bottom on limestone.
func og(_ path: String) {
    let W = 1200, H = 630
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(CARDINAL)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    ctx.setFillColor(rgb(LIME)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: 92))
    let line: CGFloat = 46, r: CGFloat = 20
    ctx.setFillColor(rgb(FOREST)); ctx.fill(CGRect(x: 0, y: line - 3, width: CGFloat(W), height: 6))
    func diamond(_ cx: CGFloat, _ cy: CGFloat, _ rx: CGFloat, _ ry: CGFloat) -> CGPath {
        let p = CGMutablePath()
        p.move(to: CGPoint(x: cx, y: cy - ry)); p.addLine(to: CGPoint(x: cx + rx, y: cy))
        p.addLine(to: CGPoint(x: cx, y: cy + ry)); p.addLine(to: CGPoint(x: cx - rx, y: cy)); p.closeSubpath()
        return p
    }
    let n = Int(CGFloat(W) / (r * 4.2))
    for i in 0..<n {
        let cx = (CGFloat(i) + 0.5) * CGFloat(W) / CGFloat(n)
        ctx.setFillColor(rgb(CARDINAL)); ctx.addPath(diamond(cx, line, r * 1.05, r * 1.25)); ctx.fillPath()
        ctx.setFillColor(CGColor(srgbRed: 1, green: 1, blue: 1, alpha: 1)); ctx.addPath(diamond(cx, line, r * 0.5, r * 0.6)); ctx.fillPath()
    }
    ctx.saveGState(); ctx.translateBy(x: 20, y: 100); cheeseDip(ctx, 500); ctx.restoreGState()
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
    let title = NSFont(name: "AvenirNextCondensed-Heavy", size: 92) ?? NSFont.boldSystemFont(ofSize: 80)
    let sub = NSFont(name: "AvenirNextCondensed-DemiBold", size: 32) ?? NSFont.boldSystemFont(ofSize: 28)
    let cream = NSColor(srgbRed: 0xF3 / 255, green: 0xEE / 255, blue: 0xE3 / 255, alpha: 1)
    let gold = NSColor(srgbRed: 0xE9 / 255, green: 0xC4 / 255, blue: 0x6A / 255, alpha: 1)
    NSAttributedString(string: "ARKANSAS", attributes: [.font: title, .foregroundColor: cream]).draw(at: NSPoint(x: 540, y: 390))
    NSAttributedString(string: "EATS", attributes: [.font: title, .foregroundColor: cream]).draw(at: NSPoint(x: 540, y: 296))
    NSAttributedString(string: "CHEESE DIP, BARBECUE & CATFISH", attributes: [.font: sub, .foregroundColor: gold]).draw(at: NSPoint(x: 544, y: 246))
    NSGraphicsContext.restoreGraphicsState()
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
og("docs/og.png")
