// Arkansas Eats icon concepts (2026-11-06), drawn in the shared Eats Ranked style (state-prompts/ICON-STYLE.md): one flat, level,
// centred food on a plain background in the state palette (cardinal #9D2235, Ozark forest #2E5E3E, limestone #F3EEE3), no backing
// shape, no text or texture; no school colours or marks (no hog, no "A"), no flag stars or text.
// Food hexes: bowl #F7F3EA, bowl shade #E2D9C6; queso #F2B33D, its top #F7C964; chip #D9A441, chip shade #C08A2E;
// fried pickle #C8893A, crust #DDA556, pickle end #7FA046; pink tomato #E8697A, its light #F08C99, calyx #8DBE5A.
//   A  a bowl of cheese dip with a tortilla chip standing in it, on cardinal
//   B  a fried dill pickle spear, breaded, its green end showing, on Ozark forest
//   C  a South Arkansas pink tomato (the state fruit and vegetable) with its green calyx, on Ozark forest
// Usage, from ar-eats/: swift scripts/icon-concepts.swift <out dir>   -> concept-{a,b,c}-1024.png
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let CARDINAL: UInt32 = 0x9D2235, FOREST: UInt32 = 0x2E5E3E, LIME: UInt32 = 0xF3EEE3
let BOWL: UInt32 = 0xF7F3EA, BOWL2: UInt32 = 0xE2D9C6, QUESO: UInt32 = 0xF2B33D, QUESO2: UInt32 = 0xF7C964
let CHIP: UInt32 = 0xD9A441, CHIP2: UInt32 = 0xC08A2E
let FRY: UInt32 = 0xC8893A, CRUST: UInt32 = 0xDDA556, PICKLE: UInt32 = 0x7FA046
let TOM: UInt32 = 0xE8697A, TOM2: UInt32 = 0xF08C99, CALYX: UInt32 = 0x8DBE5A

func R(_ s: CGFloat, _ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
    CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
}
func P(_ s: CGFloat, _ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: x * s, y: y * s) }

/// A: a bowl seen from the side (a wide rounded trapezoid), queso mounded in it, a chip standing up out of the dip. CoreGraphics y-up.
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

/// B: two breaded pickle spears lying level, one above the other, their dill-green cut ends at the right.
func friedPickle(_ c: CGContext, _ s: CGFloat) {
    for y in [0.30, 0.52] as [CGFloat] {
        c.setFillColor(rgb(PICKLE)); c.addPath(R(s, 0.66, y + 0.015, 0.19, 0.15, 0.075)); c.fillPath()
        c.setFillColor(rgb(FRY)); c.addPath(R(s, 0.15, y, 0.58, 0.18, 0.09)); c.fillPath()
        c.setFillColor(rgb(CRUST)); c.addPath(R(s, 0.21, y + 0.11, 0.44, 0.04, 0.02)); c.fillPath()   // the lighter crust on top
    }
}

/// C: a round pink tomato, slightly wider than tall, a soft highlight, and a five-point green calyx with a stem on top.
func pinkTomato(_ c: CGContext, _ s: CGFloat) {
    c.saveGState(); defer { c.restoreGState() }
    c.translateBy(x: 0, y: -0.03 * s)   // centred (check.swift)
    c.setFillColor(rgb(TOM)); c.fillEllipse(in: CGRect(x: 0.15 * s, y: 0.18 * s, width: 0.70 * s, height: 0.62 * s))
    c.setFillColor(rgb(TOM2)); c.fillEllipse(in: CGRect(x: 0.26 * s, y: 0.55 * s, width: 0.18 * s, height: 0.11 * s))
    let calyx = CGMutablePath()
    let cx = 0.50 * s, cy = 0.78 * s
    for k in 0..<10 {
        let a = CGFloat(k) * .pi / 5 + .pi / 2
        let r = (k % 2 == 0 ? 0.15 : 0.05) * s
        let p = CGPoint(x: cx + cos(a) * r, y: cy + sin(a) * r * 0.55)
        if k == 0 { calyx.move(to: p) } else { calyx.addLine(to: p) }
    }
    calyx.closeSubpath()
    c.setFillColor(rgb(CALYX)); c.addPath(calyx); c.fillPath()
    c.addPath(R(s, 0.485, 0.78, 0.03, 0.07, 0.015)); c.fillPath()   // the stem
}

func render(_ n: Int, _ path: String, _ bg: UInt32, _ draw: (CGContext, CGFloat) -> Void) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(bg)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n))
    draw(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "playbook/brand"
render(1024, out + "/concept-a-1024.png", CARDINAL, cheeseDip)
render(1024, out + "/concept-b-1024.png", FOREST, friedPickle)
render(1024, out + "/concept-c-1024.png", FOREST, pinkTomato)
