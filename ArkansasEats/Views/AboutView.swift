import SwiftUI

struct AboutView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("ARKANSAS EATS").displayFont(32).foregroundStyle(Theme.green)
                    Text("A free guide to \(model.restaurantCount.formatted()) Arkansas restaurants, with James Beard honors and hand-checked lists of Arkansas's own: the Cheese Dip Trail, barbecue, catfish houses, dairy bars and drive-ins, homemade pie, the Arkansas Food Hall of Fame and the oldest places. No account, no ads, no tracking.")
                        .font(.subheadline).foregroundStyle(Theme.ink2)
                    Text("Arkansas Eats is an independent app by Nicholas Soderstrom. It is not affiliated with, endorsed by or operated by the State of Arkansas, the Arkansas Department of Health, the Department of Finance and Administration or its Alcoholic Beverage Control, Arkansas Tourism, the Division of Arkansas Heritage or the Arkansas Food Hall of Fame, any university, the James Beard Foundation, Apple, or any restaurant or chain. Other names are trademarks of their owners.")
                        .font(.footnote).foregroundStyle(Theme.muted)
                }
                .padding(.vertical, 4)
            }
            Section("How the lists are built") {
                Text("Hand-checked lists (the Cheese Dip Trail, barbecue, catfish houses, dairy bars and drive-ins, homemade pie, the Food Hall of Fame and the oldest places) include only places checked against a 2025 or 2026 source: Arkansas Tourism's own pages, the Arkansas Food Hall of Fame or a dated local story. Founding years are the business's, as the source gives them; some places have moved since.")
                Text("Honors are facts: James Beard Foundation honors, from America's Classics to the 2025 and 2026 finalists and semifinalists, and the Arkansas Food Hall of Fame's inductees. No MICHELIN Guide covers Arkansas.")
                Text("This app starts from open map listings (Overture Maps) and keeps the kinds that proved reliable where official lists exist. Whether a place serves alcohol is unknown here, never no: a place serves alcohol only when it matches an on-premises permit on DFA Alcoholic Beverage Control's monthly list, and many counties are dry or partly dry. Adult clubs are left out, and stadium, airport and campus stands are hidden with the non-restaurants. Racing and casino resorts' restaurants are listed. Website links are checked, and any that no longer belong to the place are left out.")
                Text("Inspections: the Arkansas Department of Health inspects every food establishment in the state and gives no score or grade. Where its search lists a place, this app shows the latest inspection's date and the number of observations on ADH's report, as ADH lists them, with ADH's note that an inspection is a snapshot in time; the app computes no grade and never ranks by inspections.")
                Text("Ratings, reviews, hours and photos are Apple Maps' own, shown live in Apple's place card. This app doesn't store or rank by them.")
            }
            .font(.subheadline).foregroundStyle(Theme.ink2)
            Section("Sources") {
                source("Arkansas Department of Health", "Food establishment inspections from ADH's public search (foodserviceprod.adh.arkansas.gov), inspections from \(model.inspectionsThrough["adh"].flatMap { DayFormat.text($0) }.map { "the 12 months through " + $0 } ?? "the last 12 months"), read November 2026: each inspection's date and ADH's count of observations.", Links.inspections.absoluteString)
                source("DFA Alcoholic Beverage Control", "The full permit list (FullPermit202609.xlsx, posted \(DayFormat.text(model.permitsUpdated) ?? "October 12, 2026")): on-premises permits for \"Serves alcohol\"; no owner names are shown.", Links.licenses.absoluteString)
                source("Arkansas Food Hall of Fame", "Inductees from the Division of Arkansas Heritage's Arkansas Food Hall of Fame (arkansasheritage.com), reported as facts.", "https://www.arkansasheritage.com/arkansas-food-hall-of-fame")
                source("Overture Maps Foundation", "Restaurant listings and websites come from Overture Maps Foundation places data (overturemaps.org)\(model.overtureRelease.map { ", release \($0)" } ?? ""), filtered and reformatted for this app.\n• Data from Meta, Microsoft, DAC and BrightQuery. Available under CDLA Permissive 2.0.\n• Data from Foursquare. \(foursquareCopyright) Available under Apache 2.0. Foursquare data was transformed to the Overture schema; this app further filtered and reformatted it. See the NOTICE below.\n• Data from AllThePlaces. Available under CC0 1.0.\nResearched places are put on the map with Overture Maps addresses data (open address sources under permissive licenses, docs.overturemaps.org/attribution).", "https://overturemaps.org")
                source("Honors", "James Beard Foundation awards are reported as facts and checked by hand against the Foundation's announcements. James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation. Other names belong to their owners.", "https://www.jamesbeard.org/awards")
                source("Maps", "Maps, place cards and directions by Apple Maps.", nil)
            }
            Section("Licenses") {
                NavigationLink("Community Data License Agreement – Permissive 2.0") { LicenseText(file: "CDLA-Permissive-2.0", title: "CDLA Permissive 2.0") }
                NavigationLink("Apache License 2.0") { LicenseText(file: "Apache-2.0", title: "Apache License 2.0") }
                NavigationLink("Foursquare OS Places NOTICE") { LicenseText(file: "Foursquare-NOTICE", title: "Foursquare NOTICE") }
            }
            Section("Privacy") {
                Text("The app collects nothing. Your location, if you allow it, only sorts lists by distance and shows where you are on the map, on this device. Saved places stay on this device.")
                    .font(.subheadline).foregroundStyle(Theme.ink2)
                DataUpdatesNote()
                    .font(.footnote).foregroundStyle(Theme.muted)
                Link("Privacy policy", destination: Links.privacy)
                Link("Terms of use", destination: Links.terms)
            }
            Section("Help") {
                Link("Report a missing or closed place", destination: Links.correctionEmail)
                Link("Email \(Links.supportEmail)", destination: URL(string: "mailto:\(Links.supportEmail)")!)
                Link("Website", destination: Links.site)
                Text("Data as of \(DayFormat.text(model.generated) ?? model.generated). Places open and close; check before you go. Version \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0")")
                    .font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .navigationTitle("About")
        .tint(Theme.green)
    }

    /// the copyright line exactly as the bundled Foursquare NOTICE has it, so the two can't disagree
    private var foursquareCopyright: String {
        guard let url = Bundle.main.url(forResource: "Foursquare-NOTICE", withExtension: "txt"),
              let text = try? String(contentsOf: url, encoding: .utf8),
              let line = text.split(separator: "\n").first(where: { $0.hasPrefix("©") }) else { return "© Foursquare Labs, Inc. All rights reserved." }
        return line.trimmingCharacters(in: .whitespaces)
    }

    @ViewBuilder
    private func source(_ name: String, _ detail: String, _ url: String?) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            if let url, let u = URL(string: url) { Link(name, destination: u).font(.subheadline.weight(.semibold)) }
            else { Text(name).font(.subheadline.weight(.semibold)) }
            Text(detail).font(.caption).foregroundStyle(Theme.muted)
        }
    }
}

/// A bundled license text (Resources/Licenses), reflowed rather than shown as raw 80-column lines.
struct LicenseText: View {
    let file: String
    let title: String

    var body: some View {
        ScrollView {
            Text(text).font(.footnote).foregroundStyle(Theme.ink).textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading).padding()
        }
        .inlineTitle(title)
    }

    private var text: String {
        guard let url = Bundle.main.url(forResource: file, withExtension: "txt"),
              let raw = try? String(contentsOf: url, encoding: .utf8) else { return "License text missing." }
        // join hard-wrapped lines into paragraphs; keep blank lines and list items as breaks
        var out: [String] = []
        for para in raw.components(separatedBy: "\n\n") {
            let lines = para.components(separatedBy: "\n").map { $0.trimmingCharacters(in: .whitespaces) }
            var joined = ""
            for l in lines where !l.isEmpty {
                let startsItem = l.hasPrefix("–") || l.hasPrefix("-") || l.range(of: #"^\(?[a-z0-9]{1,3}[.)]\s"#, options: .regularExpression) != nil
                joined += joined.isEmpty ? l : (startsItem ? "\n" + l : " " + l)
            }
            if !joined.isEmpty { out.append(joined) }
        }
        return out.joined(separator: "\n\n")
    }
}
