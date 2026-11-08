import SwiftUI
import UIKit
import CoreText

/// Arkansas palette (provisional, 2026-11-06; Nick decides, playbook/05-naming.md), light only. The Razorbacks and Arkansas State
/// are both red, so a cardinal takes no side: Ozark forest #2E5E3E (7.6:1 on white) for titles, tint and accents; cardinal #9D2235
/// (white on it 7.7:1) for the hand-checked guide cards; charcoal #2B2B2B for honors chips (white 14:1); a diamond gold #E9C46A only
/// as a fill under coal #1E1E1E, never as text; limestone #F3EEE3 pages. The names `green`/`gold` are kept from Wisconsin Eats so
/// the shared views read the same; here `green` is Ozark forest and `gold` is cardinal.
enum Theme {
    static let green = Color(hex: 0x2E5E3E)      // Ozark forest: titles, tint, primary text accents
    static let green2 = Color(hex: 0x3F7652)
    static let gold = Color(hex: 0x9D2235)       // cardinal: card fills under white text
    static let goldSoft = Color(hex: 0xF5DCE0)   // soft cardinal
    static let lime = Color(hex: 0xE9C46A)       // diamond gold, fills only (hand-checked pins, the title shadow), under coal
    static let limeSoft = Color(hex: 0xF6EBCB)
    static let sand = Color(hex: 0xF3EEE3)       // the Home background, limestone
    static let red = Color(hex: 0x2B2B2B)        // charcoal: honors chips
    static let sandstone = Color(hex: 0x9D2235)  // cardinal accent (7.7:1 on white)
    static let teal = Color(hex: 0x1F6672)       // river teal accent (6.3:1 on white)
    static let ink = Color(hex: 0x1E1E1E)
    static let ink2 = Color(hex: 0x2E3440)
    static let muted = Color(hex: 0x5B6270)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xEEE8DC)
    static let surface3 = Color(hex: 0xE2DACB)
    static let rule = Color(hex: 0xE2DACB)
    static let rule2 = Color(hex: 0xCABFAE)
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "STONE CRAB", "1 MICHELIN STAR".
struct Chip: View {
    enum Style { case gold, green, red, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .green || style == .red ? Color.white : style == .dashed ? Theme.muted : style == .gold ? Theme.ink : Theme.green)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .gold ? Theme.goldSoft : style == .green ? Theme.green : style == .red ? Theme.red
                                                       : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// Arkansas Eats' lettering: the system face drawn compressed and heavy for titles and guide names, and the
/// system monospaced face for numbers, dates and small labels. No bundled fonts.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

/// Numbers, dates and small labels in the system monospaced face, scaled like DisplayFont.
struct MonoFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .semibold
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight, design: .monospaced))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }

    func monoFont(_ size: CGFloat, weight: Font.Weight = .semibold) -> some View {
        modifier(MonoFont(size: size, weight: weight))
    }
}

/// The header band: a row of diamonds (the flag's diamond, and the Crater of Diamonds) in cardinal with white centers, on an
/// Ozark-forest line.
struct Stripes: View {
    var height: CGFloat = 9

    var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height, line = h * 0.5
            ctx.fill(Path(CGRect(x: 0, y: line - 1.5, width: w, height: 3)), with: .color(Theme.green))
            let r = h * 0.48, n = max(3, Int(w / (r * 4.2)))
            func diamond(_ cx: CGFloat, _ cy: CGFloat, _ rx: CGFloat, _ ry: CGFloat) -> Path {
                var p = Path()
                p.move(to: CGPoint(x: cx, y: cy - ry)); p.addLine(to: CGPoint(x: cx + rx, y: cy))
                p.addLine(to: CGPoint(x: cx, y: cy + ry)); p.addLine(to: CGPoint(x: cx - rx, y: cy)); p.closeSubpath()
                return p
            }
            for i in 0..<n {
                let cx = (CGFloat(i) + 0.5) * w / CGFloat(n), cy = line
                ctx.fill(diamond(cx, cy, r * 1.05, r * 1.25), with: .color(Theme.gold))
                ctx.fill(diamond(cx, cy, r * 0.5, r * 0.6), with: .color(.white))
            }
        }
        .frame(height: height * 2.4)
        .accessibilityHidden(true)
    }
}

extension View {
    /// An inline navigation title in the display type. UINavigationBar.appearance() didn't reach every SwiftUI bar on iOS 27
    /// (the Map title went from compressed blue to plain black after a push and pop; place titles were always plain), so the
    /// title is our own view in the bar. The navigation title is still set, for the back button and VoiceOver.
    func inlineTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title).displayFont(19, weight: .heavy).foregroundStyle(Theme.green)
                        .lineLimit(1).minimumScaleFactor(0.7)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }
}
