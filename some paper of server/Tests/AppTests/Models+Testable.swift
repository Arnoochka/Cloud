@testable import App
import Fluent

extension User {
    static func create(
        name: String = "Luke",
        username: String = "lukes",
        on database: Database
    ) async throws -> User {
        let user = User(name: name, username: username)
        try await user.save(on: database)
        return user
    }
}

extension Acronym {
    static func create(
        short: String = "TIL",
        long: String = "Today I Learned",
        user: User? = nil,
        on database: Database
    ) async throws -> Acronym {
        var acronymsUser = user
        if acronymsUser == nil {
            acronymsUser = try await User.create(on: database)
        }
        let acronym = Acronym(
            short: short,
            long: long,
            userID: acronymsUser!.id!)
        try await acronym.save(on: database)
        return acronym
    }
}

extension App.Category {
    static func create(
        name: String = "Random",
        on database: Database
    ) async throws -> App.Category {
        let category = Category(name: name)
        try await category.save(on: database)
        return category
    }
}


