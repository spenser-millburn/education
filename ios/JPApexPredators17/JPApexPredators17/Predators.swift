//
//  Predators.swift
//  JPApexPredators17
//
//  Created by Apple on 14/04/24.
//

import Foundation

class Predators {
    var allApexPredators: [ApexPredator] = []
    var apexPredators: [ApexPredator] = []
    
    init() {
        self.decodeApexPredatorData()
    }
    
    func decodeApexPredatorData() {
        guard let url = Bundle.main.url(forResource: "jpapexpredators",
                                     withExtension: "json") else {
            return
        }
        
        do {
            let data = try Data(contentsOf: url)
            
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            
            self.allApexPredators = try decoder.decode([ApexPredator].self, from: data)
            self.apexPredators = self.allApexPredators
        } catch {
            print("Error decoding JSON data: \(error)")
        }
    }
    
    func search(for searchTerm: String) -> [ApexPredator] {
        guard !searchTerm.isEmpty else {
            return apexPredators
        }
        
        return apexPredators.filter { predator in
            predator.name.localizedCaseInsensitiveContains(searchTerm)
        }
    }
    
    func sort(by alphabatical: Bool) {
        apexPredators.sort { alphabatical ? $0.name < $1.name: $0.id < $1.id }
    }
    
    func filter(by type: PredatorType) {
        if case type = .all {
            apexPredators = allApexPredators
        } else {
            apexPredators = allApexPredators.filter { $0.type == type }
        }
    }
}
