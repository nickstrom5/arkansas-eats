import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, cheesedip, bbq, catfish, dairybar, pies, halloffame, honors, oldest, detail, map, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // Little Rock's Riverdale, among the most picks, so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 34.7600, longitude: -92.3100)
        // by name and town, ignoring case, so a rebuild with a slightly different casing still finds the place; the hand-checked one first
        let pick = { (n: String, town: String?) -> Place? in
            let hits = model.places.filter { $0.name.caseInsensitiveCompare(n) == .orderedSame && (town == nil || $0.city == town) }
            return hits.first(where: \.handChecked) ?? hits.first
        }
        for p in [pick("McClard's Bar-B-Q", "Hot Springs"), pick("Craig's Bar-B-Q", "De Valls Bluff"), pick("The Ohio Club", "Hot Springs")]
            .compactMap({ $0 }) where !model.isSaved(p) {
            model.toggleSaved(p)
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        switch name {
        case "cheesedip": open(.cheesedip)
        case "bbq": open(.bbq)
        case "catfish": open(.catfish)
        case "dairybar":
            // Benton, between Salem Dairy Bar and Garry's Sling Blade
            model.screenshotLocation = CLLocation(latitude: 34.5640, longitude: -92.5868)
            open(.dairybar)
        case "pies": open(.pies)
        case "halloffame": open(.halloffame)
        case "honors": open(.honors)
        case "oldest": open(.oldest)
        case "inspections": open(.inspections)
        case "detail":
            // McClard's: barbecue since 1928 and a Food Hall of Fame inductee, seen from across Hot Springs (about a mile off)
            model.screenshotLocation = CLLocation(latitude: 34.5080, longitude: -93.0600)
            open(.bbq)
            if let p = pick("McClard's Bar-B-Q", "Hot Springs") ?? model.places.first {
                model.selectedPlace = p; model.guidesPath.append(.place(p))
            }
        case "map":
            // downtown Little Rock: Doe's, Dizzy's and the Lassis Inn as three single pins (Riverdale's three picks share a block and
            // always cluster), the river along the top
            model.screenshotLocation = CLLocation(latitude: 34.7450, longitude: -92.2750)
            model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place": a different
        // honored or hand-checked one per shot.
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "home": pick("McClard's Bar-B-Q", "Hot Springs")
        case "cheesedip": pick("Cheers in the Heights", "Little Rock")
        case "bbq": pick("Craig's Bar-B-Q", "De Valls Bluff")
        case "catfish": pick("Catfish Hole", "Fayetteville")
        case "dairybar": pick("Salem Dairy Bar", "Benton")
        case "pies": pick("Charlotte's Eats & Sweets", "Keo")
        case "halloffame": pick("The Ohio Club", "Hot Springs")
        case "honors": pick("Lassis Inn", "Little Rock")
        case "oldest": pick("The Ohio Club", "Hot Springs")
        case "inspections": nil
        case "map": pick("Doe's Eat Place", "Little Rock")
        case "saved": pick("McClard's Bar-B-Q", "Hot Springs")
        case "about": nil
        default: pick("McClard's Bar-B-Q", "Hot Springs")
        }
        model.selectedPlace = place
    }
}
